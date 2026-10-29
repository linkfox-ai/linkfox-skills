#!/usr/bin/env python3
"""linkfox-workflow · 工作流 ↔ 多维表订阅:查看 / 启用 / 停用(方式 B,直接调订阅接口)。

一条「订阅」= 哪个工作流,挂在哪本多维表的哪张数据表上,被哪种记录事件触发。订阅生效后,
多维表记录变更 → workflow-studio 按表反查订阅 → 命中则调用该工作流。

**建立 / 修改触发配置走方式 A**(upload_workflow.py 上传时服务端按开始节点自动登记,看
stdout 的 `tableAutomation`)。本脚本只管**不动画布**的那几件事:

  list         我的订阅(可按 workflowId / 数据表 / 事件 / 启停过滤)
  by-notebook  这本多维表下挂了哪些工作流(带 --table-id 时按对该表的权限可看到他人的)
  set          启用 / 停用一条记录触发工作流的订阅;`--enabled true|false` 必填。
               定时任务(`eventType=schedule`)不接:它的启停在 Flowise 排期开关上

`set` 的请求体**从服务端那条 flow 的开始节点推导**,不接受手填的表 / 事件 / 条件:画布才是
触发配置的唯一真相源,手填一份就会和画布漂移,下次在画布上保存又被覆盖回去。开始节点已不是
记录触发时,退到该 workflow 现有的订阅行(典型场景:停用一条早先登记过的订阅)。

接口按 workflowId 幂等 upsert,同一 workflowId 重复 POST 是覆盖;**不带 enabled 就会被重新
启用**,所以本脚本永远显式发 `enabled`。没有 DELETE 接口,停用 = `enabled:false`,行不删、
多维表侧解绑,`tableSync.status` 回 `UNBOUND`。

CLI:
  python scripts/table_automation.py list [--workflow-id <id>] [--table-id tbl…]
                                          [--event-type <t>] [--enabled true|false]
  python scripts/table_automation.py by-notebook --notebook-id nbk…|__loose__ [--table-id tbl…]
  python scripts/table_automation.py set --workflow-id <id> --enabled true|false [--dry-run]
  公共可选:[--proxy-url <url>]

退出码:0 成功(set 时 = 关联已生效);1 网络 / 鉴权 / 服务端 4xx;4 写盘失败;
       64 CLI 用法错;65 响应非法 JSON;
       66 推不出订阅:开始节点不是记录触发,且这个 workflow 也没有现成订阅可启停;
          或这是挂在多维表下的定时任务(`schedule` 订阅不管排期启停,set 一律拒绝);
          或推出来的配置不完整(缺表 / 条件等),先 refine 开始节点;
       68 被拒:该 workflowId 已被别的成员绑定(409)或对触发表无权限(403);
       70 请求成功但多维表侧没登记上(tableSync 为 FAILED / SKIPPED_NO_NOTEBOOK 等),
          自动化不会跑 —— stdout 照样给出结果。
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
from table_sync import (  # type: ignore  # noqa: E402
    ALL_EVENT_TYPES,
    EVENT_TEXT,
    EVENT_TYPES,
    SCHEDULE_EVENT,
    FIELD_ID_PREFIX,
    OPERATORS,
    VALUELESS_OPERATORS,
    classify,
    schedule_context,
)
from workflow_auth import clean_key, with_auth_hint  # type: ignore  # noqa: E402


# 不用 `linkfox-workflow` 前缀:那是 workflow 文件的命名空间(basename = sourceKey)。
SLUG = "linkfox-table-automation"
API_PATH = "/api/v1/proxy/table-automations"
_UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
FLOW_TYPES = {"CHATFLOW", "AGENTFLOW", "MULTIAGENT", "ASSISTANT"}
START_NAME = "businessStartAgentflow"
# 列表摘要里每条最多带几个字段名,多了只给计数 —— stdout 是给模型读的
NAMES_MAX = 8


class AutomationError(RuntimeError):
    def __init__(self, message: str, code: int = 1, status: int | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.status = status


def _die(msg: str, code: int = 1) -> None:
    print(f"ERROR: {with_auth_hint(msg)}", file=sys.stderr)
    sys.exit(code)


def _env_first(*names: str) -> str:
    for n in names:
        v = clean_key(os.environ.get(n) or "")
        if v:
            return v
    return ""


def _bool(raw: str) -> bool:
    value = (raw or "").strip().lower()
    if value in {"true", "1", "yes"}:
        return True
    if value in {"false", "0", "no"}:
        return False
    raise argparse.ArgumentTypeError("只接受 true / false")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="View / enable / disable workflow ↔ table subscriptions")
    sub = p.add_subparsers(dest="command", required=True)

    lp = sub.add_parser("list")
    lp.add_argument("--workflow-id")
    lp.add_argument("--table-id")
    lp.add_argument("--event-type", choices=ALL_EVENT_TYPES)
    lp.add_argument("--enabled", type=_bool)
    lp.add_argument("--proxy-url")

    bp = sub.add_parser("by-notebook")
    bp.add_argument("--notebook-id", required=True)
    bp.add_argument(
        "--table-id",
        help="不是过滤器,只是权限开关:传了会先查调用者对这张表的权限,有权限时能看到他人的订阅",
    )
    bp.add_argument("--proxy-url")

    sp = sub.add_parser("set")
    sp.add_argument("--workflow-id", required=True)
    # 必填:接口不带 enabled 会被当成"启用",默认值在这里就是隐患
    sp.add_argument("--enabled", type=_bool, required=True)
    sp.add_argument("--dry-run", action="store_true", help="只打印将要发送的请求体,不调写接口")
    sp.add_argument("--proxy-url")

    args = p.parse_args(argv)
    wid = getattr(args, "workflow_id", None)
    if wid is not None and not _UUID_RE.match(wid.strip()):
        _die(f"--workflow-id 必须是工作流的 UUID:{wid!r}", 64)
    tid = getattr(args, "table_id", None)
    if tid is not None and not tid.strip().startswith("tbl"):
        _die(f"--table-id 必须以 tbl 开头:{tid!r}(nbk 开头的是多维表格,填到 --notebook-id)", 64)
    return args


# ---- HTTP -------------------------------------------------------------------


def _request(
    method: str,
    url: str,
    api_key: str,
    body: dict[str, Any] | None = None,
    timeout: int = 60,
) -> Any:
    headers = {"Authorization": api_key, "User-Agent": "LinkFox-Workflow-Agent/1.0"}
    data = None
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = Request(url, data=data, method=method, headers=headers)
    try:
        with urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
    except HTTPError as e:
        payload = e.read().decode("utf-8", errors="replace")[:400]
        raise AutomationError(_error_message(e.code, payload), status=e.code) from None
    except (URLError, TimeoutError, OSError) as e:
        raise AutomationError(f"网络失败:{e}") from None
    try:
        return json.loads(raw.decode("utf-8")) if raw else None
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise AutomationError(f"响应不是合法 JSON:{e}", code=65) from None


def _error_message(status: int, payload: str) -> str:
    try:
        parsed = json.loads(payload)
        message = parsed.get("message") if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        message = None
    # 错误 body 不保证带文案,按状态码分支是主路径
    return f"HTTP {status}: {message or payload or '(无错误文案)'}"


# ---- 摘要 / 落盘 ---------------------------------------------------------------


def _names(values: Any) -> dict[str, Any]:
    items = [str(v) for v in values] if isinstance(values, list) else []
    return {"count": len(items), "names": items[:NAMES_MAX]}


def summarize_row(row: dict[str, Any]) -> dict[str, Any]:
    event = str(row.get("eventType") or "")
    out: dict[str, Any] = {
        "workflowId": row.get("workflowId"),
        "enabled": row.get("enabled"),
        "notebookId": row.get("notebookId"),
        "tableId": row.get("tableId"),
        "eventType": event,
        "eventText": EVENT_TEXT.get(event, event),
        "createdBy": row.get("createdByMemberId"),
        "updatedAt": row.get("updatedAt"),
    }
    if event == "recordUpdated":
        out["watchFields"] = _names(row.get("watchFieldNames"))
        # 只有名字没有 id:用户改列名后订阅会静默失效
        out["watchFieldIdsMissing"] = bool(row.get("watchFieldNames")) and not row.get("watchFieldIds")
    if event == "recordConditionMet" and isinstance(row.get("condition"), dict):
        cond = row["condition"]
        out["condition"] = {k: cond.get(k) for k in ("fieldName", "operator", "value") if k in cond}
        out["conditionFieldIdMissing"] = not cond.get("fieldId")
    return out


def _persist(payload: Any) -> tuple[str, int]:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    path = os.path.abspath(resolve_data_path(SLUG, time.time(), "json"))
    tmp_path = ""
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=os.path.dirname(path),
            prefix=".table-automation-", suffix=".json.tmp", delete=False,
        ) as f:
            tmp_path = f.name
            f.write(text)
        os.replace(tmp_path, path)
    except OSError as e:
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
        raise AutomationError(f"写盘失败 {path}: {e}", code=4) from None
    return path, len(text.encode("utf-8"))


# ---- 从开始节点推导请求体 -------------------------------------------------------


def _multi(value: Any) -> list[str]:
    """多值字段既可能是真数组,也可能是 JSON 字符串(`"[\\"状态\\"]"`),两种都认。"""
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []
        try:
            value = json.loads(text)
        except json.JSONDecodeError:
            return [text]
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    return []


def _start_inputs(flow: dict[str, Any]) -> dict[str, Any] | None:
    raw = flow.get("flowData")
    try:
        data = json.loads(raw) if isinstance(raw, str) else raw
    except json.JSONDecodeError:
        raise AutomationError("服务端返回的 flowData 不是合法 JSON", code=65) from None
    for node in (data or {}).get("nodes") or []:
        nd = node.get("data") if isinstance(node, dict) else None
        if isinstance(nd, dict) and nd.get("name") == START_NAME:
            return nd.get("inputs") if isinstance(nd.get("inputs"), dict) else {}
    return None


def body_from_start(workflow_id: str, flow_type: str, inputs: dict[str, Any], enabled: bool) -> dict[str, Any]:
    """把 BusinessStart 的记录触发配置翻成订阅接口的请求体(字段名两边不同,别手抄)。"""
    event = str(inputs.get("recordEventType") or "recordCreated")
    body: dict[str, Any] = {
        "workflowId": workflow_id,
        "notebookId": str(inputs.get("notebookId") or ""),
        "tableId": str(inputs.get("tableId") or ""),
        "eventType": event,
        "flowType": flow_type,
        "enabled": enabled,
    }
    if event == "recordUpdated":
        body["watchFieldNames"] = _multi(inputs.get("recordWatchFieldNames"))
        body["watchFieldIds"] = _multi(inputs.get("recordWatchFieldIds"))
    if event == "recordConditionMet":
        # 画布上 recordConditionFieldId 是**数组**取第一项;订阅接口里 fieldId 是字符串
        ids = _multi(inputs.get("recordConditionFieldId"))
        cond: dict[str, Any] = {
            "fieldName": str(inputs.get("recordConditionFieldName") or ""),
            "operator": str(inputs.get("recordConditionOperator") or "equal"),
        }
        if ids:
            cond["fieldId"] = ids[0]
        if cond["operator"] not in VALUELESS_OPERATORS:
            cond["value"] = str(inputs.get("recordConditionValue") or "")
        body["condition"] = cond
    interval = inputs.get("recordCheckIntervalMinutes")
    if isinstance(interval, (int, float)) and not isinstance(interval, bool) and int(interval) == interval and interval > 0:
        body["checkIntervalMinutes"] = int(interval)
    return body


def body_from_row(row: dict[str, Any], enabled: bool) -> dict[str, Any]:
    """开始节点已不是记录触发时,按现有订阅行原样回发,只改 enabled。"""
    event = str(row.get("eventType") or "")
    body: dict[str, Any] = {
        "workflowId": row.get("workflowId"),
        "notebookId": row.get("notebookId") or "",
        "tableId": row.get("tableId") or "",
        "eventType": event,
        "flowType": row.get("flowType") or "AGENTFLOW",
        "enabled": enabled,
    }
    if event == "recordUpdated":
        body["watchFieldNames"] = list(row.get("watchFieldNames") or [])
        body["watchFieldIds"] = list(row.get("watchFieldIds") or [])
    if event == "recordConditionMet" and isinstance(row.get("condition"), dict):
        body["condition"] = {k: v for k, v in row["condition"].items() if v not in (None, "")}
    if isinstance(row.get("checkIntervalMinutes"), int) and row["checkIntervalMinutes"] > 0:
        body["checkIntervalMinutes"] = row["checkIntervalMinutes"]
    return body


def body_problems(body: dict[str, Any]) -> tuple[list[str], list[str]]:
    """本地预检,与服务端 400 规则对齐;发出去必然 400 / 必然不生效的直接拦下。"""
    errors: list[str] = []
    warnings: list[str] = []
    if not str(body.get("tableId") or "").startswith("tbl"):
        errors.append(f"tableId={body.get('tableId')!r} 不是数据表 id(必须以 tbl 开头)")
    if not body.get("notebookId"):
        # 服务端会 200 + SKIPPED_NO_NOTEBOOK:看着成功,自动化永远不跑
        errors.append("缺 notebookId(多维表格 nbk… / 散表 __loose__),发出去只会得到 SKIPPED_NO_NOTEBOOK")
    event = body.get("eventType")
    if event not in EVENT_TYPES:
        errors.append(f"eventType={event!r} 不支持(只支持 {' / '.join(EVENT_TYPES)})")
    for fid in body.get("watchFieldIds") or []:
        if not str(fid).startswith(FIELD_ID_PREFIX):
            errors.append(f"watchFieldIds 里的 {fid!r} 不是字段 id(必须以 fld 开头)")
    if event == "recordUpdated" and body.get("watchFieldNames") and not body.get("watchFieldIds"):
        warnings.append("监听字段只有名字没有字段 id:用户改列名后订阅会静默失效")
    if event == "recordConditionMet":
        cond = body.get("condition") or {}
        if not cond.get("fieldName"):
            errors.append("条件触发缺条件字段名")
        if cond.get("operator") not in OPERATORS:
            errors.append(f"条件算子 {cond.get('operator')!r} 非法")
        elif cond.get("operator") not in VALUELESS_OPERATORS and not str(cond.get("value") or ""):
            errors.append(f"算子 {cond.get('operator')} 需要条件值")
        if cond.get("fieldId") and not str(cond["fieldId"]).startswith(FIELD_ID_PREFIX):
            errors.append(f"条件字段 id {cond['fieldId']!r} 必须以 fld 开头")
        if cond.get("fieldName") and not cond.get("fieldId"):
            warnings.append("条件字段只有名字没有字段 id:用户改列名后订阅会静默失效")
    return errors, warnings


# ---- 子命令 -----------------------------------------------------------------


def _list_rows(proxy: str, api_key: str, **query: Any) -> list[dict[str, Any]]:
    params = {k: (str(v).lower() if isinstance(v, bool) else v) for k, v in query.items() if v is not None}
    url = proxy + API_PATH + (f"?{urlencode(params)}" if params else "")
    rows = _request("GET", url, api_key)
    if not isinstance(rows, list):
        raise AutomationError("订阅列表响应不是数组", code=65)
    return [r for r in rows if isinstance(r, dict)]


def _list_result(rows: list[dict[str, Any]], mode: str, extra: dict[str, Any]) -> dict[str, Any]:
    path, size = _persist(rows)
    return {
        "mode": mode,
        **extra,
        "total": len(rows),
        "enabledCount": sum(1 for r in rows if r.get("enabled")),
        "rows": [summarize_row(r) for r in rows],
        "path": path,
        "bytes": size,
    }


def cmd_list(args: argparse.Namespace, proxy: str, api_key: str) -> dict[str, Any]:
    rows = _list_rows(proxy, api_key, tableId=args.table_id, eventType=args.event_type, enabled=args.enabled)
    if args.workflow_id:
        # 接口不收 workflowId 过滤,客户端筛
        rows = [r for r in rows if r.get("workflowId") == args.workflow_id]
    return _list_result(rows, "list", {"workflowId": args.workflow_id} if args.workflow_id else {})


def cmd_by_notebook(args: argparse.Namespace, proxy: str, api_key: str) -> dict[str, Any]:
    query = {"notebookId": args.notebook_id, "tableId": args.table_id}
    url = f"{proxy}{API_PATH}/by-notebook?{urlencode({k: v for k, v in query.items() if v})}"
    rows = _request("GET", url, api_key)
    if not isinstance(rows, list):
        raise AutomationError("by-notebook 响应不是数组", code=65)
    rows = [r for r in rows if isinstance(r, dict)]
    scope = "所有人(调用者对该表有查看 / 编辑权限)" if args.table_id else "只含自己的订阅"
    if args.table_id and not rows:
        # 权限为 none 时也是 200 + [],与"真的没有"分不开,别报成"这本表没挂任何工作流"
        scope = "空结果:可能确实没有,也可能对该表无权限"
    return _list_result(rows, "by-notebook", {"notebookId": args.notebook_id, "scope": scope})


def cmd_set(args: argparse.Namespace, proxy: str, api_key: str) -> dict[str, Any]:
    flow = _request("GET", f"{proxy}/api/v1/chatflows/{quote(args.workflow_id, safe='')}", api_key)
    if not isinstance(flow, dict):
        raise AutomationError("工作流响应不是对象", code=65)
    flow_type = str(flow.get("type") or "AGENTFLOW").upper()
    if flow_type not in FLOW_TYPES:
        flow_type = "AGENTFLOW"
    inputs = _start_inputs(flow)
    existing = [r for r in _list_rows(proxy, api_key) if r.get("workflowId") == args.workflow_id]

    if schedule_context(inputs) or (
        existing and existing[0].get("eventType") == SCHEDULE_EVENT
        and not (inputs or {}).get("startInputType") == "tableRecordTrigger"
    ):
        # 定时订阅只记"挂在哪张表下";排期由 Flowise 调度器管,订阅的 enabled 关不掉它。
        # 在这里"停用"只会让它从多维表侧栏消失、照样按点跑 —— 比不做更糟。
        raise AutomationError(
            "这是挂在多维表下的定时任务:到点跑不跑由 Flowise 的排期开关管(画布顶部开关),"
            "与订阅的启用 / 停用无关,本脚本不改它。要停掉定时,让用户在画布顶部关掉开关;"
            "要彻底不再定时,refine 开始节点改成手动启动(带 --allow-trigger-change)",
            code=66,
        )

    if inputs is not None and inputs.get("startInputType") == "tableRecordTrigger":
        source = "canvas"
        body = body_from_start(args.workflow_id, flow_type, inputs, args.enabled)
    elif existing:
        if args.enabled:
            # 画布已不是记录触发,却要把旧订阅重新启用:下次在画布上保存又会被停掉,两边打架
            raise AutomationError(
                "开始节点已不是多维表格记录触发,不能单独重新启用旧订阅;"
                "要恢复记录触发,先 refine 开始节点(带 --allow-trigger-change)再上传",
                code=66,
            )
        source = "existingSubscription"
        body = body_from_row(existing[0], args.enabled)
    else:
        raise AutomationError(
            "这个工作流的开始节点不是多维表格记录触发,也没有现成的订阅,没有可启用 / 停用的对象",
            code=66,
        )

    errors, warnings = body_problems(body)
    before = summarize_row(existing[0]) if existing else None
    result: dict[str, Any] = {
        "mode": "set",
        "workflowId": args.workflow_id,
        "source": source,
        "before": before,
        "request": body,
        **({"warnings": warnings} if warnings else {}),
    }
    if errors:
        raise AutomationError("订阅配置不完整,拒绝发送:" + ";".join(errors), code=66)
    if args.dry_run:
        result["sent"] = False
        return result

    try:
        saved = _request("POST", proxy + API_PATH, api_key, body)
    except AutomationError as e:
        if e.status == 409:
            raise AutomationError(
                f"订阅被拒:这个工作流已被别的成员绑定,只有绑定人能启用 / 停用({e})", code=68, status=409
            ) from None
        if e.status == 403:
            # 不留 "HTTP 403" 字样:with_auth_hint 会把它当成 API Key 问题,给错排查方向
            detail = str(e).replace("HTTP 403", "status 403")
            raise AutomationError(f"订阅被拒:对触发数据表没有权限({detail})", code=68, status=403) from None
        raise
    sync = (saved or {}).get("tableSync") if isinstance(saved, dict) else None
    status = sync.get("status") if isinstance(sync, dict) else None
    info = classify(status)
    if isinstance(sync, dict) and sync.get("detail"):
        info["detail"] = sync["detail"]  # 给人看的失败原因,原样转述,不解析
    result.update({
        "sent": True,
        "after": summarize_row(saved) if isinstance(saved, dict) else None,
        "tableSync": info,
    })
    return result


COMMANDS = {"list": cmd_list, "by-notebook": cmd_by_notebook, "set": cmd_set}


def main(argv: list[str] | None = None) -> None:
    try:
        sys.stdout.reconfigure(line_buffering=True)  # type: ignore[attr-defined]
    except AttributeError:
        pass
    args = _parse_args(argv)
    api_key = _env_first("LINKFOX_AGENT_API_KEY", "LINKFOXAGENT_API_KEY")
    if not api_key:
        _die("missing LinkFox API key; set LINKFOX_AGENT_API_KEY", 1)
    proxy = ((args.proxy_url or "").strip() or get_api_base()).rstrip("/")
    try:
        summary = COMMANDS[args.command](args, proxy, api_key)
    except AutomationError as e:
        _die(str(e), e.code)
        return
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if summary.get("path"):
        print(f"Saved full response: {summary['path']} ({summary['bytes']} bytes)")
    sync = summary.get("tableSync")
    if isinstance(sync, dict) and not sync.get("effective"):
        # 请求成功、行已落库,但多维表侧没登记上:stdout 已给结果,用退出码把"没生效"说死
        print(f"ERROR: 订阅已保存,但多维表侧未生效(tableSync.status={sync.get('status')}):{sync.get('meaning')}",
              file=sys.stderr)
        sys.exit(70)


if __name__ == "__main__":
    main()
