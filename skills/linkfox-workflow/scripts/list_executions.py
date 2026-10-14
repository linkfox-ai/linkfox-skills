#!/usr/bin/env python3
"""linkfox-workflow · 查看一份 linkfox-workflow 系统工作流的执行记录。

用于用户问"这个流程跑过几次 / 最近一次跑成功了吗 / 上次为什么失败 / 看下执行记录"时,
通过 workflow-studio 代理读 linkfox-workflow 系统的 Executions API,并把完整响应落到会话 workspace。

**这是纯读动作**,不触发执行、不改 flow、不删记录。

两种模式(二选一,互斥):
  - 列表:`--workflow-id <flowId>` → GET /api/v1/executions?agentflowId=<flowId>&page&limit
    可选 `--state` / `--session-id` / `--start-date` / `--end-date` 过滤。
    返回 `{data: [...], total}`;每条记录含 id / state / createdDate / stoppedDate /
    sessionId,以及体积很大的 `executionData` —— 摘要里**不含** executionData,只给计数。
  - 详情:`--execution-id <executionId>` → GET /api/v1/executions/<executionId>
    返回单条记录,`executionData` 是逐节点执行轨迹(字符串化 JSON);脚本会解析它并派生
    每个节点的 status 与错误信息。

state 取值(linkfox-workflow 系统的 `ExecutionState`,权威):`INPROGRESS` / `FINISHED` / `ERROR` /
`TERMINATED` / `TIMEOUT` / `STOPPED`。**这里的 state 才是权威运行状态**,
`run_workflow.py` 的 runStatus 只是当次响应的派生值。

租户隔离由服务端负责:服务端按 API Key 解析出所属成员 / 租户并过滤 executions,
拿不到别的成员 / 别的租户的记录,脚本不需要也不应该自己再过滤。

CLI:
  python scripts/list_executions.py \
    (--workflow-id <flowId> | --execution-id <executionId>)
    [--state FINISHED]              # 仅列表模式
    [--session-id <id>]             # 仅列表模式
    [--start-date 2026-08-01]       # 仅列表模式,ISO 日期或日期时间
    [--end-date 2026-08-25]         # 仅列表模式
    [--page 1] [--limit 12]         # 仅列表模式,limit 上限 50
    [--inline]                      # stdout 追加完整响应(默认只回摘要)
    [--proxy-url <url>]             # 同 upload_workflow.py
    [--node-io <nodeId|显示名>]      # 仅详情模式。取该节点实际的 input / output / error,
                                    #   脱敏后单独落盘,stdout 给路径 + 预览
    [--max-chars 2000]              # --node-io 预览长度(100..20000),超出标 truncated

退出码:0 成功;1 网络 / 鉴权 / 未找到(含 --node-io 指定的节点这次没执行到);
       4 写盘失败;64 CLI 用法错;65 响应非法 JSON。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from linkfox_paths import get_api_base, resolve_data_path  # type: ignore  # noqa: E402
from workflow_auth import clean_key, with_auth_hint  # type: ignore  # noqa: E402


# 同 run_workflow.py:不用 `linkfox-workflow` 前缀,避免被 save_workflow.py 误认成 workflow 文件。
EXEC_SLUG = "linkfox-executions"
_FLOWID_RE = re.compile(r"^[A-Za-z0-9_-]{6,64}$")
_EXECID_RE = re.compile(r"^[A-Za-z0-9_-]{6,64}$")
# 与 linkfox-workflow 系统的执行状态枚举逐字一致。
EXECUTION_STATES = (
    "INPROGRESS",
    "FINISHED",
    "ERROR",
    "TERMINATED",
    "TIMEOUT",
    "STOPPED",
)
LIMIT_MAX = 50
SMALL_THRESHOLD = 8000
ERROR_PREVIEW_CHARS = 400


def _die(msg: str, code: int = 1) -> None:
    print(f"ERROR: {with_auth_hint(msg)}", file=sys.stderr)
    sys.exit(code)


def _env_first(*names: str) -> str:
    for n in names:
        v = clean_key(os.environ.get(n) or "")
        if v:
            return v
    return ""


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Read linkfox-workflow execution records through workflow-studio"
    )
    p.add_argument("--workflow-id")
    p.add_argument("--execution-id")
    p.add_argument("--state")
    p.add_argument("--session-id")
    p.add_argument("--start-date")
    p.add_argument("--end-date")
    p.add_argument("--page", type=int, default=1)
    p.add_argument("--limit", type=int, default=12)
    p.add_argument("--inline", action="store_true")
    p.add_argument("--proxy-url")
    p.add_argument("--node-io")
    p.add_argument("--max-chars", type=int, default=NODE_IO_PREVIEW_DEFAULT)
    args = p.parse_args(argv)

    if args.node_io is not None:
        if not args.execution_id:
            _die("--node-io 只能配合 --execution-id(先从列表里拿到 executionId)", 64)
        if not args.node_io.strip():
            _die("--node-io 需要 nodeId 或节点显示名", 64)
        if args.inline:
            _die("--node-io 不能与 --inline 同用:完整响应未脱敏,不进 stdout", 64)
    if args.max_chars < 100 or args.max_chars > 20000:
        _die(f"--max-chars 必须在 100..20000 之间,当前 {args.max_chars}", 64)

    if bool(args.workflow_id) == bool(args.execution_id):
        _die(
            "--workflow-id 与 --execution-id 二选一:列表用 --workflow-id,"
            "单条详情用 --execution-id",
            64,
        )
    if args.workflow_id and not _FLOWID_RE.match(args.workflow_id):
        _die(f"--workflow-id 格式非法:{args.workflow_id!r}", 64)
    if args.execution_id and not _EXECID_RE.match(args.execution_id):
        _die(f"--execution-id 格式非法:{args.execution_id!r}", 64)
    if args.execution_id:
        for flag, value in (
            ("--state", args.state),
            ("--session-id", args.session_id),
            ("--start-date", args.start_date),
            ("--end-date", args.end_date),
        ):
            if value:
                _die(f"{flag} 只在列表模式(--workflow-id)下有效", 64)
    if args.state:
        normalized = args.state.strip().upper()
        if normalized not in EXECUTION_STATES:
            _die(
                f"--state 必须是 {'/'.join(EXECUTION_STATES)} 之一,当前 {args.state!r}",
                64,
            )
        args.state = normalized
    if args.page < 1:
        _die(f"--page 必须 ≥ 1,当前 {args.page}", 64)
    if args.limit < 1 or args.limit > LIMIT_MAX:
        _die(f"--limit 必须在 1..{LIMIT_MAX} 之间,当前 {args.limit}", 64)
    return args


def _resolve_api_key() -> str:
    api_key = _env_first("LINKFOX_AGENT_API_KEY", "LINKFOXAGENT_API_KEY")
    if not api_key:
        _die("missing LinkFox API key; set LINKFOX_AGENT_API_KEY", 1)
    return api_key


def _proxy_url(cli: str | None) -> str:
    """API 基础地址:CLI `--proxy-url` > `linkfox_paths.get_api_base()`。

    地址来源只有 `get_api_base()` 一处(env `LINKFOX_TOOL_GATEWAY`,缺省
    正式网关)—— 与其余 90+ 个 linkfox skill 共用同一个
    函数,本 skill 不另立环境变量、也不硬编码地址。
    """
    return ((cli or "").strip() or get_api_base()).rstrip("/")


def _headers(api_key: str) -> dict[str, str]:
    return {
        "Authorization": api_key,
        "User-Agent": "LinkFox-Workflow-Agent/1.0",
    }


def _get_json(url: str, headers: dict[str, str], timeout: int = 60) -> Any:
    req = Request(url, method="GET", headers=headers)
    try:
        with urlopen(req, timeout=timeout) as resp:
            body = resp.read()
            status = resp.status
    except HTTPError as e:
        payload = e.read().decode("utf-8", errors="replace")[:400]
        if e.code == 404:
            _die(f"未找到执行记录 (HTTP 404: {payload})", 1)
        _die(f"读执行记录失败 HTTP {e.code}: {payload}", 1)
        raise  # unreachable
    except (URLError, TimeoutError, OSError) as e:
        _die(f"读执行记录网络失败:{e}", 1)
        raise  # unreachable
    if not 200 <= status < 300:
        _die(f"读执行记录失败 HTTP {status}", 1)
    try:
        return json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        _die(f"执行记录响应不是合法 JSON:{e}", 65)
        raise  # unreachable


def _parse_execution_data(raw: Any) -> list[Any]:
    """executionData 在 linkfox-workflow 系统里以字符串化 JSON 存储;解析失败就当空轨迹。"""
    if isinstance(raw, list):
        return raw
    if isinstance(raw, str) and raw.strip():
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            return []
        return parsed if isinstance(parsed, list) else []
    return []


def summarize_trace(execution_data: Any) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    """把 executionData 压成逐节点状态 + 报错清单;不带节点输出内容(可能极大)。"""
    trace = _parse_execution_data(execution_data)
    nodes: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for item in trace:
        if not isinstance(item, dict):
            continue
        node_id = str(item.get("nodeId") or "")
        label = str(item.get("nodeLabel") or "")
        status = str(item.get("status") or "")
        entry: dict[str, Any] = {"nodeId": node_id, "nodeLabel": label, "status": status}
        payload = item.get("data")
        error_text = ""
        if isinstance(payload, dict):
            raw_error = payload.get("error")
            if isinstance(raw_error, str) and raw_error.strip():
                error_text = raw_error.strip()
            elif isinstance(raw_error, dict):
                error_text = str(raw_error.get("message") or raw_error)
        if error_text:
            entry["error"] = error_text[:ERROR_PREVIEW_CHARS]
        if status.upper() == "ERROR" or error_text:
            errors.append(
                {
                    "nodeId": node_id,
                    "nodeLabel": label,
                    "error": (error_text or "节点状态为 ERROR,但记录未带错误详情")[
                        :ERROR_PREVIEW_CHARS
                    ],
                }
            )
        nodes.append(entry)
    return nodes, errors


# ---- 单节点输入 / 输出(--node-io) -------------------------------------------
#
# 默认不给节点 IO(几百 KB 的轨迹会灌爆上下文),但"节点实际吃到了什么、吐出了什么"是
# 验证"节点干对了"的唯一证据。没有这个出口,调用方只能自己写临时脚本去抠落盘文件。
# 所以开一个窄口:只取指定节点,脱敏后单独落盘,stdout 只给截断预览。
#
# 脱敏是硬要求:节点输入里会带飞书 / 钉钉 webhook、加签密钥、鉴权头。按字段名命中就整值
# 替换;字段名没命中、但值本身是机器人 webhook 地址的也替换。

_SENSITIVE_KEY_RE = re.compile(
    r"(secret|token|password|passwd|apikey|api_key|authorization|webhook|credential|cookie)",
    re.IGNORECASE,
)
_SENSITIVE_VALUE_RE = re.compile(
    r"https?://[^\s\"']*(?:open\.feishu\.cn|open\.larksuite\.com|oapi\.dingtalk\.com|"
    r"qyapi\.weixin\.qq\.com)[^\s\"']*",
    re.IGNORECASE,
)
REDACTED = "***已脱敏***"
NODE_IO_PREVIEW_DEFAULT = 2000


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        # HTTP 节点的 headers / queryParams 是 [{key, value}] 形态:敏感的是 key 指向的 value。
        pair_key = value.get("key")
        if (
            isinstance(pair_key, str)
            and _SENSITIVE_KEY_RE.search(pair_key)
            and value.get("value") not in (None, "")
        ):
            return {**{k: redact(v) for k, v in value.items() if k != "value"}, "value": REDACTED}
        return {
            k: (REDACTED if isinstance(k, str) and _SENSITIVE_KEY_RE.search(k) and v not in (None, "")
                else redact(v))
            for k, v in value.items()
        }
    if isinstance(value, list):
        return [redact(v) for v in value]
    if isinstance(value, str):
        return _SENSITIVE_VALUE_RE.sub(REDACTED, value)
    return value


def extract_node_io(execution_data: Any, node_ref: str) -> dict[str, Any] | None:
    """按 nodeId 或 nodeLabel 取一个节点的 input / output / error。找不到返回 None。

    同一节点在 Loop / Iteration 里可能执行多次,全部按顺序返回在 `runs[]` 里。
    """
    runs: list[dict[str, Any]] = []
    matched_id = ""
    matched_label = ""
    for item in _parse_execution_data(execution_data):
        if not isinstance(item, dict):
            continue
        nid = str(item.get("nodeId") or "")
        label = str(item.get("nodeLabel") or "")
        if node_ref not in (nid, label):
            continue
        matched_id, matched_label = nid, label
        payload = item.get("data") if isinstance(item.get("data"), dict) else {}
        runs.append(
            redact(
                {
                    "status": str(item.get("status") or ""),
                    "input": payload.get("input"),
                    "output": payload.get("output"),
                    "error": payload.get("error"),
                }
            )
        )
    if not runs:
        return None
    return {"nodeId": matched_id, "nodeLabel": matched_label, "runs": runs}


def summarize_record(record: dict[str, Any], with_trace: bool) -> dict[str, Any]:
    """单条执行记录的摘要。永远不把 executionData 原文放进 stdout。"""
    agentflow = record.get("agentflow")
    entry: dict[str, Any] = {
        "executionId": str(record.get("id") or ""),
        "state": str(record.get("state") or ""),
        "sessionId": str(record.get("sessionId") or ""),
        "createdDate": str(record.get("createdDate") or ""),
        "stoppedDate": str(record.get("stoppedDate") or ""),
        "updatedDate": str(record.get("updatedDate") or ""),
    }
    if isinstance(agentflow, dict):
        entry["agentflowId"] = str(agentflow.get("id") or "")
        entry["agentflowName"] = str(agentflow.get("name") or "")
    elif record.get("agentflowId"):
        entry["agentflowId"] = str(record["agentflowId"])
    nodes, errors = summarize_trace(record.get("executionData"))
    entry["nodeCount"] = len(nodes)
    if with_trace:
        entry["nodes"] = nodes
    if errors:
        entry["nodeErrors"] = errors
    if record.get("action"):
        # HumanInput 等待人工时 action 非空;这是"卡在人工审批"的信号,不是失败。
        entry["pendingAction"] = True
    return entry


def _write_atomic(path: str, content: str) -> None:
    tmp_path = ""
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=os.path.dirname(path),
            prefix=".workflow-exec-",
            suffix=".json.tmp",
            delete=False,
        ) as f:
            tmp_path = f.name
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    except OSError as e:
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
        _die(f"写执行记录失败 {path}: {e}", 4)


def _list_url(proxy: str, args: argparse.Namespace) -> str:
    params: dict[str, str] = {
        "agentflowId": args.workflow_id,
        "page": str(args.page),
        "limit": str(args.limit),
    }
    if args.state:
        params["state"] = args.state
    if args.session_id:
        params["sessionId"] = args.session_id
    if args.start_date:
        params["startDate"] = args.start_date
    if args.end_date:
        params["endDate"] = args.end_date
    return f"{proxy}/api/v1/executions?{urlencode(params)}"


def main() -> None:
    try:
        sys.stdout.reconfigure(line_buffering=True)  # type: ignore[attr-defined]
        sys.stderr.reconfigure(line_buffering=True)  # type: ignore[attr-defined]
    except AttributeError:
        pass

    args = _parse_args()
    api_key = _resolve_api_key()
    proxy = _proxy_url(args.proxy_url)
    headers = _headers(api_key)

    summary: dict[str, Any] = {}

    if args.execution_id:
        url = f"{proxy}/api/v1/executions/{quote(args.execution_id, safe='')}"
        payload = _get_json(url, headers)
        if not isinstance(payload, dict):
            _die("执行详情响应顶层必须是对象", 65)
        summary["mode"] = "detail"
        summary["execution"] = summarize_record(payload, with_trace=True)
        if args.node_io is not None:
            node_ref = args.node_io.strip()
            io = extract_node_io(payload.get("executionData"), node_ref)
            if io is None:
                known = [n["nodeId"] for n in summary["execution"].get("nodes", [])]
                _die(
                    f"这次执行里没有节点 {node_ref!r}(按 nodeId 或显示名匹配);"
                    f"本次执行到的节点:{known}。没出现在这里的节点就是这次没执行到",
                    1,
                )
            io_text = json.dumps(io, ensure_ascii=False, indent=2)
            io_path = os.path.abspath(resolve_data_path(EXEC_SLUG + "-nodeio", time.time(), "json"))
            _write_atomic(io_path, io_text)
            summary["mode"] = "node-io"
            summary["nodeIo"] = {
                "nodeId": io["nodeId"],
                "nodeLabel": io["nodeLabel"],
                "runCount": len(io["runs"]),
                "path": io_path,
                "preview": io_text[: args.max_chars],
                "truncated": len(io_text) > args.max_chars,
                "redacted": REDACTED in io_text,
            }
    else:
        payload = _get_json(_list_url(proxy, args), headers)
        if not isinstance(payload, dict):
            _die("执行列表响应顶层必须是对象", 65)
        records = payload.get("data")
        if not isinstance(records, list):
            _die("执行列表响应缺少 data 数组", 65)
        summary["mode"] = "list"
        summary["workflowId"] = args.workflow_id
        summary["total"] = payload.get("total")
        summary["page"] = args.page
        summary["limit"] = args.limit
        summary["returned"] = len(records)
        if args.state:
            summary["stateFilter"] = args.state
        summary["executions"] = [
            summarize_record(r, with_trace=False) for r in records if isinstance(r, dict)
        ]

    full = json.dumps(payload, ensure_ascii=False, indent=2)
    out_path = os.path.abspath(resolve_data_path(EXEC_SLUG, time.time(), "json"))
    _write_atomic(out_path, full)
    summary["path"] = out_path
    summary["bytes"] = len(full.encode("utf-8"))

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    # --node-io 模式不回显完整响应:那份是未脱敏的原文。
    if args.node_io is None and (args.inline or summary["bytes"] <= SMALL_THRESHOLD):
        print("--- full response ---")
        print(full)
    print(f"Saved full response: {out_path} ({summary['bytes']} bytes)")


if __name__ == "__main__":
    main()
