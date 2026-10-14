#!/usr/bin/env python3
"""linkfox-workflow · 执行一份已经在 linkfox-workflow 系统上的 agentflow v2 工作流。

用于用户明确说"跑一下这个流程 / 执行这个工作流 / 试跑一次"时,通过 workflow-studio
代理调 linkfox-workflow 系统的 Prediction API 真实跑一次,并把完整响应落到会话 workspace。

**执行是有副作用的动作**。flow 里的 SendNotification 会真的发通知,WriteFile 会真的
写多维表,HTTP / LinkfoxHTTP 会真的打外部接口。因此本脚本只在用户明确要求执行时才
允许调用 —— 不得在 generate / refine 上传成功后"顺手跑一下验证"。

流程:
  1. 从环境读取 LinkFox API Key + 代理地址(与 upload/fetch 一致)。
  2. GET /api/v1/chatflows/<workflowId> 校验 flow 存在,拿到展示名与 type;
     type 不是 AGENTFLOW 时拒绝执行(本 skill 只管 agentflow v2)。
  3. POST /api/v1/prediction/<workflowId>,body 按 IncomingAgentflowInput 构造,
     **不带 streaming** —— linkfox-workflow 系统于是返回一次性 JSON 而不是 SSE 流。
  4. 完整响应落到会话 data/,再从 agentFlowExecutedData 派生逐节点状态摘要。
  5. stdout 返回摘要(runStatus / executionId / chatId / text / 节点状态 / path)。

**runStatus 是派生值,不是 linkfox-workflow 系统的 Execution.state**:由各节点 status 汇总而来。
  - 任一节点 status == "ERROR"                   → ERROR
  - 响应带 action(流程停在 HumanInput 等人工)  → WAITING_HUMAN_INPUT
  - 其余                                          → FINISHED
拿权威状态请用 `list_executions.py --execution-id <executionId>`。
**runStatus 不是 FINISHED 时不得对用户说"执行成功"。**

BusinessStart 的运行时约定:`startInputType=chatInput`(手动启动)会把 question 强制归一
为空串,所以手动启动的 flow 不传 `--question` 就行。`formInput` / `webhookTrigger` 形态
用 `--form-file` / `--webhook-file` 传入参。

CLI:
  python scripts/run_workflow.py \
    --workflow-id <flowId>              # 必填。来自 <linkfox-flow-info id="..."/>
    [--question <text>]                # 可选。默认空串
    [--form-file <path>]               # 可选。formInput 触发的表单值(JSON 对象)
    [--webhook-file <path>]            # 可选。webhookTrigger 的 payload(JSON 对象)
    [--override-config-file <path>]    # 可选。overrideConfig(JSON 对象)
    [--session-id <id>]                # 可选。复用同一会话上下文
    [--timeout <seconds>]              # 可选。默认 300,上限 900
    [--inline]                         # 可选。stdout 追加完整响应(默认只回摘要)
    [--proxy-url <url>]                # 可选。同 upload_workflow.py
    [--expect-reached <nodeId>]        # 可选,可重复。断言该节点这次必须执行到且没失败
    [--expect-not-reached <nodeId>]    # 可选,可重复。断言该节点这次不应执行
    [--skip-preflight]                 # 可选。用户明确坚持带着缺口试跑时才用

执行前检查(run_preflight.py):按 flow 实际用到的节点查必需资源(模型 / 表 / 店铺 /
专家 / 子流程 / 通知目标;linkfoxAgentApi 凭据后台自动绑定,不查),有缺口就列出"节点 → 缺什么"并退出 66,不调 Prediction API。

执行后 stdout 额外给出 notReachedNodes(没执行到的节点)、actionResults(通知 / 写表 /
专家自报的业务状态)、triggerNote(非手动启动的手动执行说明);带 --expect-* 时再给
assertions 与 businessCheck(PASS / FAIL)。**FINISHED 不等于业务验收通过。**

退出码:0 调用成功(flow 内部报错体现在 runStatus/nodeErrors,仍为 0);
       1 网络 / 鉴权 / flow 不存在 / flow 类型不对;3 响应缺 executionId;
       4 写盘失败;64 CLI 用法错 / --expect-* 引用了不存在的节点;65 响应非法 JSON;
       66 执行前检查发现缺必需资源(未执行)。
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
from urllib.parse import quote
from urllib.request import Request, urlopen


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from linkfox_paths import get_api_base, resolve_data_path  # type: ignore  # noqa: E402
from workflow_auth import clean_key, with_auth_hint  # type: ignore  # noqa: E402
from run_preflight import (  # type: ignore  # noqa: E402
    action_results,
    evaluate_assertions,
    exec_nodes,
    not_reached,
    parse_flow_data,
    preflight,
    start_input_type,
)


# 落盘 slug 故意不以 `linkfox-workflow` 开头:save_workflow.py 的
# _GENERATED_FILENAME_RE 认那个前缀,run 产物长得像 workflow 文件只会制造误判。
RUN_SLUG = "linkfox-run"
_FLOWID_RE = re.compile(r"^[A-Za-z0-9_-]{6,64}$")
TIMEOUT_DEFAULT = 300
TIMEOUT_MAX = 900
# 与 linkfox 三大规范一致:超过这个字节数就只回摘要,完整内容永远在落盘文件里。
SMALL_THRESHOLD = 8000
TEXT_PREVIEW_CHARS = 1200


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
        description="Run one linkfox-workflow agentflow v2 through workflow-studio"
    )
    p.add_argument("--workflow-id", required=True)
    p.add_argument("--question", default="")
    p.add_argument("--form-file")
    p.add_argument("--webhook-file")
    p.add_argument("--override-config-file")
    p.add_argument("--session-id")
    p.add_argument("--timeout", type=int, default=TIMEOUT_DEFAULT)
    p.add_argument("--inline", action="store_true")
    p.add_argument("--proxy-url")
    p.add_argument("--skip-preflight", action="store_true")
    p.add_argument("--expect-reached", action="append", default=[])
    p.add_argument("--expect-not-reached", action="append", default=[])
    args = p.parse_args(argv)
    if not _FLOWID_RE.match(args.workflow_id):
        _die(f"--workflow-id 格式非法:{args.workflow_id!r}", 64)
    if args.timeout < 1 or args.timeout > TIMEOUT_MAX:
        _die(f"--timeout 必须在 1..{TIMEOUT_MAX} 秒之间,当前 {args.timeout}", 64)
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


def _request(
    method: str,
    url: str,
    headers: dict[str, str],
    json_body: dict[str, Any] | None = None,
    timeout: int = 60,
) -> tuple[int, bytes]:
    body = None
    request_headers = dict(headers)
    if json_body is not None:
        body = json.dumps(json_body, ensure_ascii=False).encode("utf-8")
        request_headers["Content-Type"] = "application/json"
    req = Request(url, data=body, headers=request_headers, method=method.upper())
    try:
        with urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read()
    except HTTPError as e:
        return e.code, e.read()
    except (URLError, TimeoutError, OSError) as e:
        _die(f"{method} {url} 网络失败:{e}", 1)
        raise  # unreachable, keeps type checkers happy


def _excerpt(body: bytes, limit: int = 400) -> str:
    return body.decode("utf-8", errors="replace")[:limit]


def _load_json_object(path: str, flag: str) -> dict[str, Any]:
    if not os.path.isfile(path):
        _die(f"{flag} 指向的文件不存在:{path}", 64)
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except OSError as e:
        _die(f"读 {flag} 失败:{e}", 64)
    except json.JSONDecodeError as e:
        _die(f"{flag} 不是合法 JSON:{e.msg} (line {e.lineno} col {e.colno})", 64)
    if not isinstance(data, dict):
        _die(f"{flag} 顶层必须是 JSON 对象", 64)
    return data


def _verify_flow(
    proxy: str, headers: dict[str, str], flow_id: str
) -> tuple[str, str]:
    """校验 flow 存在且是 agentflow v2;返回 (name, type)。"""
    name, flow_type, _ = _load_flow(proxy, headers, flow_id)
    return name, flow_type


def _load_flow(
    proxy: str, headers: dict[str, str], flow_id: str
) -> tuple[str, str, dict[str, Any] | None]:
    """校验 flow 存在且是 agentflow v2;返回 (name, type, flowData 对象或 None)。"""
    status, body = _request(
        "GET", f"{proxy}/api/v1/chatflows/{quote(flow_id, safe='')}", headers
    )
    if status == 404:
        _die(f"workflowId 未找到:{flow_id};无法执行不存在的工作流", 1)
    if not 200 <= status < 300:
        _die(f"校验 workflow 失败 HTTP {status}: {_excerpt(body)}", 1)
    try:
        flow = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        _die(f"workflow 响应不是合法 JSON:{e}", 65)
    if not isinstance(flow, dict):
        _die("workflow 响应顶层必须是对象", 65)
    flow_type = str(flow.get("type") or "").strip().upper()
    if flow_type and flow_type != "AGENTFLOW":
        _die(
            f"workflowId {flow_id} 的类型是 {flow_type},不是 AGENTFLOW;"
            "本 skill 只执行 agentflow v2",
            1,
        )
    return (
        str(flow.get("name") or "").strip(),
        flow_type or "AGENTFLOW",
        parse_flow_data(flow),
    )


# 手动执行时拿不到真实事件载荷的启动方式。执行照跑,但 stdout 带上这句,
# 免得把"手动跑通"说成"事件触发配好了"。
_NO_PAYLOAD_TRIGGERS = {
    "storeAuthorization": "店铺授权启动手动执行没有真实店铺事件载荷;跑通不代表事件触发已生效",
    "tableRecordTrigger": (
        "记录触发手动执行没有变更载荷(recordEvent / rows / recordRows 不存在);"
        "跑通不代表记录触发已生效,接了 WriteFile 的会报'没有产出任何记录'"
    ),
    "scheduleInput": "这是手动触发的一次,不代表定时任务已登记或已按时自动执行",
}


def _check_expected_ids(
    flow_data: dict[str, Any] | None, ids: list[str]
) -> None:
    """断言里写的 nodeId 必须真实存在 —— 写错 id 的断言永远'没执行到',会被误读。"""
    if not ids:
        return
    if flow_data is None:
        _die("拿不到该 workflow 的 flowData,无法校验 --expect-* 里的节点 id", 1)
    known = {n["nodeId"] for n in exec_nodes(flow_data)}
    unknown = [i for i in ids if i not in known]
    if unknown:
        _die(f"--expect-* 引用了 flow 里不存在的节点:{unknown}", 64)


def _build_body(args: argparse.Namespace) -> dict[str, Any]:
    """按 linkfox-workflow 系统的 IncomingAgentflowInput 构造请求体。

    不设置 `streaming`:linkfox-workflow 系统侧 `isStreamingRequested` 只认显式 true,
    缺省即走一次性 JSON 响应,正好是脚本要的形态。
    """
    body: dict[str, Any] = {"question": args.question or ""}
    if args.form_file:
        body["form"] = _load_json_object(args.form_file, "--form-file")
    if args.webhook_file:
        body["webhook"] = _load_json_object(args.webhook_file, "--webhook-file")
    if args.override_config_file:
        body["overrideConfig"] = _load_json_object(
            args.override_config_file, "--override-config-file"
        )
    if args.session_id:
        body["sessionId"] = args.session_id
    return body


def summarize_nodes(executed: Any) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    """把 agentFlowExecutedData 压成逐节点摘要 + 报错清单。

    `data` 字段(INodeExecutionData)可能很大,只留 status 与错误信息;完整内容看落盘文件。
    """
    nodes: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    if not isinstance(executed, list):
        return nodes, errors
    for item in executed:
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
                error_text = str(raw_error.get("message") or raw_error)[:400]
        if error_text:
            entry["error"] = error_text[:400]
        if status.upper() == "ERROR" or error_text:
            errors.append(
                {
                    "nodeId": node_id,
                    "nodeLabel": label,
                    "error": error_text or "节点状态为 ERROR,但响应未带错误详情",
                }
            )
        nodes.append(entry)
    return nodes, errors


def derive_run_status(result: dict[str, Any], node_errors: list[dict[str, str]]) -> str:
    """派生本次执行的整体状态。报错优先于人工等待 —— 错了就是错了。"""
    if node_errors:
        return "ERROR"
    if result.get("action"):
        return "WAITING_HUMAN_INPUT"
    return "FINISHED"


def _write_atomic(path: str, content: str) -> None:
    tmp_path = ""
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=os.path.dirname(path),
            prefix=".workflow-run-",
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
        _die(f"写执行结果失败 {path}: {e}", 4)


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

    flow_name, flow_type, flow_data = _load_flow(proxy, headers, args.workflow_id)
    _check_expected_ids(flow_data, args.expect_reached + args.expect_not_reached)

    # 执行前检查:缺必需资源的 flow 跑了也必然在那个节点失败,前面节点的副作用却已发生。
    if flow_data is not None and not args.skip_preflight:
        problems = preflight(flow_data)
        if problems:
            print(
                json.dumps(
                    {
                        "workflowId": args.workflow_id,
                        "name": flow_name,
                        "preflight": "MISSING_RESOURCES",
                        "missing": problems,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
            for p in problems:
                print(
                    f"ERROR: 节点「{p['nodeLabel']}」({p['nodeId']}) 缺:{'、'.join(p['missing'])}",
                    file=sys.stderr,
                )
            print(
                "ERROR: 未执行。请用户在 linkfox-workflow 系统里补齐上述配置后再跑;"
                "用户明确坚持带缺口试跑时才加 --skip-preflight",
                file=sys.stderr,
            )
            sys.exit(66)

    body = _build_body(args)

    started = time.time()
    status, raw = _request(
        "POST",
        f"{proxy}/api/v1/prediction/{quote(args.workflow_id, safe='')}",
        headers,
        json_body=body,
        timeout=args.timeout,
    )
    elapsed_ms = int((time.time() - started) * 1000)

    if not 200 <= status < 300:
        _die(f"执行 workflow 失败 HTTP {status}: {_excerpt(raw)}", 1)
    try:
        result = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        _die(f"执行响应不是合法 JSON:{e}", 65)
    if not isinstance(result, dict):
        _die("执行响应顶层必须是对象", 65)

    execution_id = str(result.get("executionId") or "").strip()
    if not execution_id:
        _die("执行响应缺少 executionId;无法确认这次运行已被记录", 3)

    full = json.dumps(result, ensure_ascii=False, indent=2)
    out_path = os.path.abspath(resolve_data_path(RUN_SLUG, time.time(), "json"))
    _write_atomic(out_path, full)

    nodes, node_errors = summarize_nodes(result.get("agentFlowExecutedData"))
    run_status = derive_run_status(result, node_errors)
    text = result.get("text")
    text_str = text if isinstance(text, str) else ""

    summary: dict[str, Any] = {
        "path": out_path,
        "workflowId": args.workflow_id,
        "name": flow_name,
        "flowType": flow_type,
        "runStatus": run_status,
        "executionId": execution_id,
        "chatId": str(result.get("chatId") or ""),
        "elapsedMs": elapsed_ms,
        "bytes": len(full.encode("utf-8")),
        "nodeCount": len(nodes),
        "nodes": nodes,
        "textPreview": text_str[:TEXT_PREVIEW_CHARS],
        "textTruncated": len(text_str) > TEXT_PREVIEW_CHARS,
    }
    if result.get("sessionId"):
        summary["sessionId"] = str(result["sessionId"])
    if node_errors:
        summary["nodeErrors"] = node_errors
    if run_status == "WAITING_HUMAN_INPUT":
        summary["pendingAction"] = result.get("action")

    # 业务层证据:FINISHED 只代表没节点报错,不代表该做的动作做了。
    executed = result.get("agentFlowExecutedData")
    if flow_data is not None:
        summary["notReachedNodes"] = not_reached(executed, flow_data)
        trigger_note = _NO_PAYLOAD_TRIGGERS.get(start_input_type(flow_data))
        if trigger_note:
            summary["triggerNote"] = trigger_note
    actions = action_results(executed, flow_data)
    if actions:
        summary["actionResults"] = actions
    if args.expect_reached or args.expect_not_reached:
        assertions = evaluate_assertions(
            executed, args.expect_reached, args.expect_not_reached, actions
        )
        summary["assertions"] = assertions
        summary["businessCheck"] = (
            "PASS" if run_status == "FINISHED" and all(a["pass"] for a in assertions) else "FAIL"
        )

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if args.inline or summary["bytes"] <= SMALL_THRESHOLD:
        print("--- full response ---")
        print(full)
    if run_status == "ERROR":
        print(
            f"WARN: 本次执行有 {len(node_errors)} 个节点报错;不要对用户说执行成功。",
            file=sys.stderr,
        )
    failed_actions = [a for a in actions if a.get("status") == "error"]
    if failed_actions:
        print(
            f"WARN: {len(failed_actions)} 个动作节点自报 status=error(通知 / 写表 / 专家);"
            "执行状态是 FINISHED 也不能说动作成功。",
            file=sys.stderr,
        )
    if summary.get("businessCheck") == "FAIL":
        print("WARN: 业务断言未通过;不要对用户说验收通过。", file=sys.stderr)
    print(f"Saved full response: {out_path} ({summary['bytes']} bytes)")


if __name__ == "__main__":
    main()
