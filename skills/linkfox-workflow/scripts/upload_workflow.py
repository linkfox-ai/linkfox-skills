#!/usr/bin/env python3
"""Upload or update one linkfox-workflow agentflow v2 JSON through workflow-studio.

The sequence:
  1. Authenticate with the LinkFox API key only (the server resolves member/group from it).
  2. Resolve the target flowId, in this order of authority:
       a. ``--workflow-id`` passed by the caller,
       b. the sourceKey -> flowId mapping on workflow-studio (server),
       c. the local ``workflow-index.json`` binding for this exact file — last resort only.
     Nothing resolves by display name: names are editable and duplicated, so matching
     on one risks overwriting an unrelated workflow.
  3. PUT the existing flow or POST a new one.
  4. Persist the flowId <-> file binding, verify the mapping, and return the ID.
  5. Version history (best effort, never fails the upload): an update first PATCHes
     ``/version-history`` on so the pre-change content is recorded, then reads the new
     version number from the PUT response headers; a create turns history on right after
     the POST. Reported as ``history`` in the stdout payload.
     The binding is written before verification on purpose: the flow already exists at
     that point, so a retry after a mapping failure must update it, not create a copy.
  6. Table automation (方式 A): when the Start node is a 多维表格记录触发 — or a 定时启动
     carrying ``linkfoxTableAutomationContext`` (``eventType=schedule``) — the server
     registers the subscription on the same POST/PUT and reports it in the
     ``X-Table-Automation-Sync`` header. Reported as ``tableAutomation``; a non-effective
     status (FAILED / SKIPPED_NO_NOTEBOOK / notSaved) does **not** fail the upload — the
     flow is saved, only the automation won't run — so exit stays 0 and the caller must
     read ``tableAutomation.effective``.

**The linkfox-workflow flowId is the workflow's identity, not the filename.** ``sourceKey``
is only the basename of the local file, and that basename carries a microsecond
timestamp — so any re-save under a new name would miss the server-side
``(group, member, sourceKey, flowType)`` unique key and silently POST a duplicate
workflow. Step 2b closes that hole on the server side — the side that owns the truth.
The local binding in 2c is consulted **after** the server, never before: it survives only
as a net for the case where the server mapping is gone (a create whose mapping write
failed leaves the caller without any workflowId to retry with).

Before any network call the file must pass the save gate (``workflow_identity.check_uploadable``):
it has to be exactly what the last successful ``save_workflow.py`` wrote, and that last save must
have finished. Otherwise exit 65 — a failed save must never be followed by uploading the stale file
that is still on disk.

The script never prints credentials. On success ``main`` prints the result
JSON (``workflowId``, ``action``, ``name``, ``flowType``, ``sourceKey``,
``mappingStatus``) to stdout with exit code 0 — callers must read that
payload as authoritative and never re-verify by running extra lookups.
Failures exit non-zero and never emit a success payload.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)
from linkfox_paths import get_api_base  # type: ignore  # noqa: E402
from table_sync import (  # type: ignore  # noqa: E402
    SCHEDULE_EVENT,
    SCHEDULE_TABLE_PLACEHOLDER,
    SYNC_HEADER,
    classify as classify_table_sync,
    schedule_context,
)
from workflow_auth import clean_key, with_auth_hint  # type: ignore  # noqa: E402
from workflow_identity import (  # type: ignore  # noqa: E402
    check_uploadable,
    forget as forget_flow_binding,
    lookup_by_flow_id as lookup_flow_binding_by_id,
    lookup_by_path as lookup_flow_id_by_path,
    register as register_flow_binding,
)

FLOW_TYPE_DEFAULT = "AGENTFLOW"
TRANSIENT_HTTP_CODES = {408, 429, 500, 502, 503, 504}


class UploadError(RuntimeError):
    """A safe, user-displayable upload failure."""


class UploadGateError(UploadError):
    """The file is not the version the last successful save produced (exit 65)."""


@dataclass(frozen=True)
class HttpResult:
    status: int
    headers: dict[str, str]
    body: bytes

    def json(self) -> Any:
        if not self.body:
            return None
        try:
            return json.loads(self.body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise UploadError(
                f"HTTP {self.status} returned invalid JSON: {_body_excerpt(self.body)}"
            ) from exc


def _body_excerpt(body: bytes, limit: int = 400) -> str:
    return body.decode("utf-8", errors="replace")[:limit]


def _env_first(*names: str) -> str:
    for name in names:
        value = clean_key(os.environ.get(name) or "")
        if value:
            return value
    return ""


def get_linkfox_api_key() -> str:
    api_key = _env_first("LINKFOX_AGENT_API_KEY", "LINKFOXAGENT_API_KEY")
    if not api_key:
        raise UploadError(
            "missing LinkFox API key; set LINKFOX_AGENT_API_KEY"
        )
    return api_key


def get_proxy_url(cli_value: str | None) -> str:
    """API 基础地址:CLI `--proxy-url` > `linkfox_paths.get_api_base()`。

    地址来源只有 `get_api_base()` 一处(env `LINKFOX_TOOL_GATEWAY`,缺省
    正式网关)—— 与其余 90+ 个 linkfox skill 共用同一个
    函数,本 skill 不另立环境变量、也不硬编码地址。
    """
    return ((cli_value or "").strip() or get_api_base()).rstrip("/")


def _request(
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    json_body: dict[str, Any] | None = None,
    timeout: int = 120,
    retries: int = 3,
) -> HttpResult:
    body = None
    request_headers = dict(headers or {})
    if json_body is not None:
        body = json.dumps(json_body, ensure_ascii=False).encode("utf-8")
        request_headers.setdefault("Content-Type", "application/json")
    elif method.upper() == "POST":
        body = b""

    last_error = "request failed"
    for attempt in range(retries):
        if attempt:
            time.sleep(1 << (attempt - 1))
        request = Request(url, data=body, headers=request_headers, method=method.upper())
        try:
            with urlopen(request, timeout=timeout) as response:
                return HttpResult(
                    status=response.status,
                    headers={key.lower(): value for key, value in response.headers.items()},
                    body=response.read(),
                )
        except HTTPError as exc:
            response_body = exc.read()
            result = HttpResult(
                status=exc.code,
                headers={key.lower(): value for key, value in exc.headers.items()},
                body=response_body,
            )
            if exc.code not in TRANSIENT_HTTP_CODES or attempt == retries - 1:
                return result
            last_error = f"HTTP {exc.code}: {_body_excerpt(response_body)}"
        except (URLError, TimeoutError, OSError) as exc:
            last_error = f"connection failed: {exc}"
            if attempt == retries - 1:
                break
    raise UploadError(last_error)


def _linkfox_headers(
    linkfox_api_key: str,
    source_key: str | None = None,
) -> dict[str, str]:
    headers = {
        "Authorization": linkfox_api_key,
        "User-Agent": "LinkFox-Workflow-Agent/1.0",
    }
    if source_key is not None:
        headers["x-workflow-source-key"] = source_key
    return headers


def _mapping_url(proxy_url: str, source_key: str, flow_type: str) -> str:
    encoded_key = quote(source_key, safe="")
    return (
        f"{proxy_url}/api/v1/proxy/workflow-mappings/{encoded_key}?"
        + urlencode({"flowType": flow_type})
    )


def find_existing_flow_id(
    proxy_url: str,
    linkfox_api_key: str,
    source_key: str,
    flow_type: str,
    content_path: str = "",
) -> str:
    """Resolve the flowId to update, or "" to create a new flow.

    Authority order is server-first:
      1. the server-side ``sourceKey`` mapping,
      2. the local ``workflow-index.json`` binding for this exact file — only as a
         last-resort net for the case where the server mapping is missing/dangling.
    Display names never participate — see the comment at the bottom.

    Why the server goes first: the local index is a cache, and the local file is not
    the source of truth (users edit the canvas and fill in credentials in the UI).
    The local tier is kept rather than dropped because it is the only thing that
    prevents a second copy when the server mapping write failed at create time — a
    run that fails ``verify_mapping`` exits non-zero without ever handing the caller
    a workflowId, so a retry has nothing else to go on.
    """
    auth_headers = _linkfox_headers(linkfox_api_key)

    mapping_url = _mapping_url(proxy_url, source_key, flow_type)
    mapping_response = _request("GET", mapping_url, headers=auth_headers)
    existing_id = ""

    if mapping_response.status == 200:
        mapping = mapping_response.json()
        if isinstance(mapping, dict):
            existing_id = str(mapping.get("flowId") or "").strip()
    elif mapping_response.status != 404:
        raise UploadError(
            f"workflow mapping lookup failed: HTTP {mapping_response.status}: "
            f"{_body_excerpt(mapping_response.body)}"
        )

    if existing_id:
        verify = _request(
            "GET",
            f"{proxy_url}/api/v1/chatflows/{quote(existing_id, safe='')}",
            headers=auth_headers,
        )
        if verify.status == 404:
            # The mapped flow is gone on linkfox-workflow; the mapping is dangling. Drop it and
            # fall through.
            _request("DELETE", mapping_url, headers=auth_headers, retries=1)
            existing_id = ""
        elif not 200 <= verify.status < 300:
            raise UploadError(
                f"cannot verify mapped flowId {existing_id}: HTTP {verify.status}; "
                "mapping was preserved to avoid creating a duplicate workflow"
            )
        else:
            return existing_id

    # Last resort, after the server said nothing: this exact file was already uploaded
    # once and bound to a flowId locally. The binding survives renames and new sessions.
    if content_path:
        bound_id, _ = lookup_flow_id_by_path(content_path)
        if bound_id:
            verify = _request(
                "GET",
                f"{proxy_url}/api/v1/chatflows/{quote(bound_id, safe='')}",
                headers=auth_headers,
            )
            if 200 <= verify.status < 300:
                return bound_id
            if verify.status == 404:
                # The flow was deleted on linkfox-workflow; drop the stale binding and fall through.
                forget_flow_binding(bound_id)
            else:
                raise UploadError(
                    f"cannot verify locally bound flowId {bound_id}: HTTP {verify.status}; "
                    "refusing to create a duplicate workflow"
                )

    # No third "match by name + type" tier on purpose.
    #
    # Display names are not identities: they are user-facing, editable, and freely
    # duplicated across a group. Recovering a flowId by name means that when someone
    # else's workflow happens to share this name, we PUT over it and report success —
    # silently destroying unrelated data. The upside it bought (recovering when the
    # server-side mapping was lost but the flow existed) is now covered by
    # workflow-index.json, which keys on the flowId we actually created.
    #
    # With this tier gone, the worst case is an extra orphan flow the user can delete.
    # That is strictly better than an overwrite nobody notices.
    return ""


def import_workflow(
    proxy_url: str,
    linkfox_api_key: str,
    flow_data: str,
    flow_name: str,
    source_key: str,
    flow_type: str,
    existing_id: str,
) -> tuple[str, str, str, dict[str, str]]:
    payload = {"name": flow_name, "type": flow_type, "flowData": flow_data}
    headers = _linkfox_headers(linkfox_api_key, source_key)
    if existing_id:
        action = "updated"
        response = _request(
            "PUT",
            f"{proxy_url}/api/v1/chatflows/{quote(existing_id, safe='')}",
            headers=headers,
            json_body=payload,
            retries=1,
        )
    else:
        action = "created"
        response = _request(
            "POST",
            proxy_url + "/api/v1/chatflows",
            headers=headers,
            json_body=payload,
            retries=1,
        )

    if not 200 <= response.status < 300:
        raise UploadError(_save_failure_message(action, response))
    data = response.json()
    response_id = str(data.get("id") or "").strip() if isinstance(data, dict) else ""
    workflow_id = response_id or existing_id
    if not workflow_id:
        raise UploadError("linkfox-workflow upload succeeded but response did not contain an id")
    mapping_status = response.headers.get("x-workflow-mapping-status", "")
    return workflow_id, action, mapping_status, response.headers


HISTORY_STATUS_HEADER = "x-chatflow-history-status"
VERSION_HEADER = "x-chatflow-version"


def _version_from(headers: dict[str, str]) -> int | None:
    raw = (headers.get(VERSION_HEADER) or "").strip()
    return int(raw) if raw.isdigit() else None


def enable_history(proxy_url: str, linkfox_api_key: str, workflow_id: str) -> dict[str, Any]:
    """打开该 workflow 的历史记录,返回 {enabled, status, version}。**从不抛错**。

    产品口径是"skill 建的、改的流都开历史"。打开时服务端把**当前内容**记成一版(内容和最新一版
    相同就不重复记),响应头带回那一版的版本号 —— 更新前调用,拿到的就是"AI 改之前"的版本号,
    撤销时还原到它。

    只有属主能开关(协作者 403):打不开不影响上传,如实返回 enabled=False。
    """
    try:
        result = _request(
            "PATCH",
            f"{proxy_url}/api/v1/chatflows/{quote(workflow_id, safe='')}/version-history",
            headers=_linkfox_headers(linkfox_api_key),
            json_body={"enabled": True},
            timeout=30,
            retries=1,
        )
    except UploadError as exc:
        return {"enabled": None, "status": "error", "error": str(exc)[:200]}
    if result.status == 403:
        return {"enabled": False, "status": "forbidden"}
    if result.status == 404:
        # 服务端还没有历史记录接口(老版本 Flowise),不当错误
        return {"enabled": None, "status": "unsupported"}
    if not 200 <= result.status < 300:
        return {"enabled": None, "status": "error", "error": f"HTTP {result.status}"}
    out: dict[str, Any] = {
        "enabled": True,
        "status": result.headers.get(HISTORY_STATUS_HEADER) or "unknown",
    }
    version = _version_from(result.headers)
    if version is not None:
        out["version"] = version
    return out


def summarize_history(
    action: str,
    before: dict[str, Any] | None,
    save_headers: dict[str, str],
    after_create: dict[str, Any] | None,
) -> dict[str, Any]:
    """把上传前后几次调用的结果归一成 stdout 的 `history` 字段。

    - created:POST 本身不记历史,紧接着打开开关,那一版(BASELINE)就是这次生成的内容。
    - updated:PUT 之前已经打开过开关(`before`),PUT 响应头给出这次保存是第几版;
      `previousVersion` 是改之前那一版,撤销就还原到它。
    """
    if action == "created":
        info = dict(after_create or {"enabled": None, "status": "unknown"})
        return info
    info: dict[str, Any] = {}
    status = (save_headers.get(HISTORY_STATUS_HEADER) or "").strip()
    version = _version_from(save_headers)
    info["status"] = status or "unknown"
    info["enabled"] = True if status in {"recorded", "unchanged", "failed"} else (
        False if status == "disabled" else (before or {}).get("enabled")
    )
    if version is not None:
        info["version"] = version
    previous = (before or {}).get("version")
    if isinstance(previous, int) and status == "recorded" and previous != version:
        info["previousVersion"] = previous
    if before and before.get("status") == "forbidden":
        info["enableForbidden"] = True
    return info


# 保存被拒时服务端给的业务码(错误 body 不保证带文案,所以只做"认得出就翻译"的增强)。
# 刻意不写 "HTTP 403" 字样:那会被 with_auth_hint 当成 API Key 问题,给出错误的排查方向。
_SAVE_REJECT_HINTS = {
    "no_table_permission": "当前账号对开始节点选的触发数据表没有权限,换一张自己有编辑权限的表",
    "read_only_workflow": "这个工作流对当前账号是只读的(不是属主),不能保存",
    "tenant has no member mapping": "账号的租户映射缺失,需要平台侧处理,重试无效",
}


def _save_failure_message(action: str, response: HttpResult) -> str:
    excerpt = _body_excerpt(response.body)
    if response.status in (403, 409):
        for code, hint in _SAVE_REJECT_HINTS.items():
            if code in excerpt:
                return f"linkfox-workflow workflow {action} rejected ({code}, status {response.status}): {hint}"
        if response.status == 409:
            return (
                f"linkfox-workflow workflow {action} rejected (status 409): 这个工作流的多维表订阅已被别的成员绑定,"
                f"只有绑定人能改它的触发配置。服务端原文:{excerpt}"
            )
    return f"linkfox-workflow workflow {action} request failed: HTTP {response.status}: {excerpt}"


def _start_inputs(flow_data: str) -> dict[str, Any] | None:
    try:
        flow = json.loads(flow_data)
    except json.JSONDecodeError:
        return None
    for node in flow.get("nodes") or []:
        data = node.get("data") if isinstance(node, dict) else None
        if isinstance(data, dict) and data.get("name") == "businessStartAgentflow":
            return data.get("inputs") if isinstance(data.get("inputs"), dict) else {}
    return None


def _table_binding(flow_data: str) -> dict[str, Any] | None:
    """开始节点会登记多维表订阅时返回 `{kind, notebookId, tableId}`,否则 None。

    两类:记录触发(`tableRecordTrigger`,表 id 在 Start 上);挂在多维表下的定时启动
    (`scheduleInput` + `linkfoxTableAutomationContext`,表 id 在上下文里)。
    """
    inputs = _start_inputs(flow_data)
    if inputs is None:
        return None
    if inputs.get("startInputType") == "tableRecordTrigger":
        return {"kind": "record", "notebookId": inputs.get("notebookId") or "",
                "tableId": inputs.get("tableId") or ""}
    ctx = schedule_context(inputs)
    if ctx:
        return {"kind": SCHEDULE_EVENT, **ctx}
    return None


def summarize_table_automation(flow_data: str, save_headers: dict[str, str]) -> dict[str, Any] | None:
    """方式 A 的关联结果。返回 None = 这次保存与多维表无关(stdout 不出现该字段)。"""
    raw = (save_headers.get(SYNC_HEADER) or "").strip()
    binding = _table_binding(flow_data)
    if raw:
        info = classify_table_sync(raw, kind=binding["kind"] if binding else "record")
        if binding:
            info["notebookId"] = binding["notebookId"]
            info["tableId"] = binding["tableId"]
            if binding["kind"] == SCHEDULE_EVENT:
                info["eventType"] = SCHEDULE_EVENT
                if not str(binding["tableId"]).startswith("tbl") or str(binding["tableId"]).startswith("tbl__"):
                    # 服务端存成占位 tbl__schedule__:挂在多维表下,但归不到具体表,权限闸门也不探
                    info["tableIdPlaceholder"] = SCHEDULE_TABLE_PLACEHOLDER
        return info
    if binding:
        # 开始节点会登记订阅,服务端却没回关联头:说不清登记上没有,不能替用户说"已生效"
        what = "记录触发" if binding["kind"] == "record" else "挂在多维表下的定时启动"
        return {
            "status": "",
            "effective": None,
            "meaning": (
                f"开始节点是{what},但服务端没有返回关联结果;用 "
                "table_automation.py list --workflow-id <id> 查订阅是否在、是否启用"
            ),
        }
    return None


def verify_mapping(
    proxy_url: str,
    linkfox_api_key: str,
    source_key: str,
    flow_type: str,
    workflow_id: str,
    mapping_status: str,
) -> None:
    response = _request(
        "GET",
        _mapping_url(proxy_url, source_key, flow_type),
        headers=_linkfox_headers(linkfox_api_key),
    )
    if response.status != 200:
        raise UploadError(
            "linkfox-workflow upload succeeded but mapping verification failed "
            f"(workflowId={workflow_id}, header={mapping_status or 'missing'}, "
            f"HTTP {response.status})"
        )
    mapping = response.json()
    mapped_id = str(mapping.get("flowId") or "").strip() if isinstance(mapping, dict) else ""
    mapped_key = str(mapping.get("sourceKey") or "") if isinstance(mapping, dict) else ""
    mapped_type = str(mapping.get("flowType") or "") if isinstance(mapping, dict) else ""
    if (mapped_id, mapped_key, mapped_type) != (workflow_id, source_key, flow_type):
        raise UploadError(
            "linkfox-workflow upload succeeded but mapping values do not match "
            f"(workflowId={workflow_id})"
        )
    if mapping_status != "saved":
        raise UploadError(
            "linkfox-workflow upload and mapping lookup succeeded, but proxy did not return "
            f"X-Workflow-Mapping-Status: saved (workflowId={workflow_id})"
        )


def load_workflow(path: str) -> str:
    file_path = Path(path).expanduser()
    if not file_path.is_file():
        raise UploadError(f"workflow file does not exist: {file_path}")
    try:
        text = file_path.read_text(encoding="utf-8").strip()
        data = json.loads(text)
    except OSError as exc:
        raise UploadError(f"cannot read workflow file: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise UploadError(
            f"workflow JSON is invalid: {exc.msg} (line {exc.lineno}, col {exc.colno})"
        ) from exc
    if not isinstance(data, dict):
        raise UploadError("workflow JSON top level must be an object")
    required = {"description", "usecases", "nodes", "edges"}
    if set(data) != required:
        raise UploadError(
            "workflow JSON top level must contain only description/usecases/nodes/edges"
        )
    return json.dumps(data, ensure_ascii=False, indent=4)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Idempotently upload a linkfox-workflow agentflow v2 JSON"
    )
    parser.add_argument("--content-file", required=True)
    parser.add_argument(
        "--name",
        default="",
        help=(
            "linkfox-workflow workflow display name, shown in the user's workflow list. "
            "Required on create: falling back to the filename stem would surface "
            "'linkfox-workflow-demo-1787554771874002' as the workflow's name. With "
            "--workflow-id it may be omitted; the name last recorded for that id is reused "
            "(reported as nameReused). It never falls back to the filename."
        ),
    )
    parser.add_argument("--flow-type", default=FLOW_TYPE_DEFAULT)
    parser.add_argument("--proxy-url")
    parser.add_argument(
        "--workflow-id",
        default="",
        help=(
            "Explicit linkfox-workflow flowId to PUT into; use when refining a workflow fetched "
            "by fetch_workflow.py so we bypass sourceKey mapping lookup and update the "
            "exact same flow the user referenced via <linkfox-flow-info id=...>. Omitting "
            "it is safe for a file already bound in workflow-index.json — the binding is "
            "consulted before the sourceKey mapping."
        ),
    )
    return parser.parse_args(argv)


def run(args: argparse.Namespace) -> dict[str, Any]:
    content_path = str(Path(args.content_file).expanduser())
    # 保存→上传门禁:只上传"最近一次 save_workflow.py 成功落盘、之后没被动过"的那份文件。
    # 放在任何网络调用之前 —— 被拒时线上 flow 一个字节都没变。
    uploadable, why = check_uploadable(content_path)
    if not uploadable:
        raise UploadGateError(
            f"拒绝上传 {content_path}:{why}。先修好片段、重跑 save_workflow.py 直到退出码 0,"
            "再上传它 stdout 里的 path;不要上传旧文件"
        )
    flow_data = load_workflow(content_path)
    flow_name = (args.name or "").strip()
    name_reused = False
    if not flow_name and (getattr(args, "workflow_id", "") or "").strip():
        # 更新已有 flow 时沿用索引里上次的展示名。名字不参与身份解析,沿用它不会认领别的 flow;
        # 绝不回退到文件名。
        bound = lookup_flow_binding_by_id((args.workflow_id or "").strip())
        flow_name = str((bound or {}).get("name") or "").strip()
        name_reused = bool(flow_name)
    # The real persisted filename is the workflow identity. Refinements overwrite the
    # same path, so this value stays stable and mapping lookup resolves the same flowId.
    source_key = Path(content_path).name.strip()
    flow_type = (args.flow_type or FLOW_TYPE_DEFAULT).strip().upper()
    if not flow_name:
        raise UploadError(
            "workflow name cannot be empty: pass --name '<业务展示名>' "
            "(首次创建必填;更新时索引里也没有记录上次的名字)"
        )
    if not source_key or "/" in source_key or "\\" in source_key:
        raise UploadError("source-key must be a non-empty filename, not a path")
    if not source_key.endswith(".json"):
        raise UploadError("source-key must include the .json suffix")
    if flow_type not in {"AGENTFLOW", "CHATFLOW"}:
        raise UploadError("flow-type must be AGENTFLOW or CHATFLOW")

    linkfox_api_key = get_linkfox_api_key()
    proxy_url = get_proxy_url(args.proxy_url)
    explicit_workflow_id = (getattr(args, "workflow_id", "") or "").strip()
    if explicit_workflow_id:
        # Refining a fetched flow: caller already told us the exact target flowId,
        # so skip mapping resolution and PUT straight into it.
        auth_headers = _linkfox_headers(linkfox_api_key)
        verify = _request(
            "GET",
            f"{proxy_url}/api/v1/chatflows/{quote(explicit_workflow_id, safe='')}",
            headers=auth_headers,
        )
        if verify.status == 404:
            raise UploadError(
                f"--workflow-id {explicit_workflow_id} not found on linkfox-workflow; refuse to "
                "create a new workflow silently"
            )
        if not 200 <= verify.status < 300:
            raise UploadError(
                f"cannot verify --workflow-id {explicit_workflow_id}: HTTP {verify.status}"
            )
        existing_id = explicit_workflow_id
    else:
        existing_id = find_existing_flow_id(
            proxy_url, linkfox_api_key, source_key, flow_type,
            content_path,
        )
    # 更新前先确保历史记录开着:改之前的内容先记成一版,这次改动才单独成为一版、可以撤销。
    history_before = enable_history(proxy_url, linkfox_api_key, existing_id) if existing_id else None
    workflow_id, action, mapping_status, save_headers = import_workflow(
        proxy_url,
        linkfox_api_key,
        flow_data,
        flow_name,
        source_key,
        flow_type,
        existing_id,
    )
    # Record the binding BEFORE verifying the mapping, not after.
    #
    # The flow now exists on linkfox-workflow. If mapping verification fails below, this run
    # raises — and without a binding written here, the next run would find nothing
    # locally, miss the server-side mapping too, and POST a second copy. Writing the
    # binding first makes a retry update the flow we just created. The binding is a
    # local cache, so recording a flow that exists is always correct, whatever the
    # mapping ends up saying.
    register_flow_binding(workflow_id, content_path, flow_name, flow_type)
    verify_mapping(
        proxy_url,
        linkfox_api_key,
        source_key,
        flow_type,
        workflow_id,
        mapping_status,
    )
    history_after = enable_history(proxy_url, linkfox_api_key, workflow_id) if action == "created" else None
    table_automation = summarize_table_automation(flow_data, save_headers)
    return {
        "workflowId": workflow_id,
        "action": action,
        "name": flow_name,
        "flowType": flow_type,
        "sourceKey": source_key,
        "mappingStatus": "saved",
        **({"nameReused": True} if name_reused else {}),
        # 历史记录是附加信息:任何一步失败都不影响上传成功的判定
        "history": summarize_history(action, history_before, save_headers, history_after),
        # 与多维表关联的结果(方式 A);未生效也不让上传失败 —— flow 已经存好了
        **({"tableAutomation": table_automation} if table_automation else {}),
    }


def main() -> None:
    # Line-buffer so a background-shell caller sees the JSON immediately.
    try:
        sys.stdout.reconfigure(line_buffering=True)  # type: ignore[attr-defined]
        sys.stderr.reconfigure(line_buffering=True)  # type: ignore[attr-defined]
    except AttributeError:
        pass
    try:
        result = run(_parse_args())
    except UploadGateError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(65)
    except UploadError as exc:
        print(f"ERROR: {with_auth_hint(str(exc))}", file=sys.stderr)
        raise SystemExit(1)
    # Explicit success payload: skill callers read `workflowId` / `mappingStatus`
    # straight from stdout. A silent exit forces them to re-query the mapping,
    # which is expensive and can loop.
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(
        f"Uploaded workflow: workflowId={result['workflowId']} action={result['action']} "
        f"mappingStatus={result['mappingStatus']}"
    )
    automation = result.get("tableAutomation")
    if automation and automation.get("effective") is False:
        # 保存成功但自动化不会跑:单独一行,别让调用方只看到上面那句 "Uploaded" 就报成功
        print(
            f"WARNING: 工作流已保存,但多维表自动化未生效(tableAutomation.status="
            f"{automation.get('status')}):{automation.get('meaning')}",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
