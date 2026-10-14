#!/usr/bin/env python3
"""智能表格-修改工作流触发表 - LinkFox Skill
调用 /smartTable/updateWorkflowTriggerTable 接口。

改（或清空）一条已登记工作流的触发数据表。

⚠️ tableId **必填但可为 null**：null = 解绑（这条流不再被触发）。
   不能用「省略字段」表达解绑 —— 那样一次手滑就静默停掉一条自动化。
⚠️ 两种结果都是 errcode 200，必须看 status：
   updated = 改了；not_found = 我们这边没有这个 flowId 的关联，什么都没改。
⚠️ 但权限不足是真的 403，不会伪装成 not_found。
⚠️ 原触发表被删除时**不需要**调这条 —— 后端已自动置空。

Usage:
  python smart_table.py updateWorkflowTriggerTable '{"flowId":"f1","tableId":"tblXXX"}'
  python smart_table.py updateWorkflowTriggerTable '{"flowId":"f1","tableId":null}' --inline
"""

import json
import os
import sys
import time
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API_PATH = "/smartTable/updateWorkflowTriggerTable"
SLUG = "linkfox-smart-table-update-workflow-trigger-table"

# 响应 <= 该字节数时落盘后额外全量打印到 stdout；超过则只打摘要
SMALL_THRESHOLD = 8000

# linkfox_paths.py 由 scaffold 从 linkfoxagent-v2/_shared 复制到本目录 scripts/，原样不改。
from linkfox_paths import get_api_base, resolve_data_path


def get_api_url():
    return get_api_base() + API_PATH


def get_api_key():
    key = os.environ.get("LINKFOX_AGENT_API_KEY") or os.environ.get("LINKFOXAGENT_API_KEY")
    if not key:
        print(
            "API Key not configured. Please complete authorization first:\n"
            "1. Visit https://agent.linkfox.com -> 设置 -> API KEY to obtain your Key\n"
            "2. Set the environment variable: export LINKFOX_AGENT_API_KEY=your-key-here",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


def call_api(params):
    req = Request(
        get_api_url(),
        data=json.dumps(params, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": get_api_key(),  # 值即 key 本身，不加任何前缀
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "LinkFox-Skill/2.0",
            "SESSION_ID": os.environ.get("SESSION_ID", ""),
            "MESSAGE_ID": os.environ.get("MESSAGE_ID", ""),
            "MODE_ID": os.environ.get("MODE_ID", ""),
            "APP_NAME": os.environ.get("APP_NAME", ""),
        },
        method="POST",
    )
    try:
        with urlopen(req, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        try:
            return json.loads(body) if body else {"errcode": e.code, "errmsg": f"HTTP {e.code}: {e.reason}"}
        except Exception:
            return {"errcode": e.code, "errmsg": f"HTTP {e.code}: {e.reason}", "details": body}
    except URLError as e:
        return {"errcode": 0, "errmsg": f"Connection failed: {e.reason}"}


def summarize(result):
    """打印紧凑摘要。这个接口的响应很小，正常走不到这里。"""
    if not isinstance(result, dict):
        print(f"Response type: {type(result).__name__}")
        print(json.dumps(result, ensure_ascii=False)[:500])
        return
    print(f"Top-level keys: {list(result.keys())}")
    for k in ("errcode", "errmsg", "status", "flowId", "notebookId", "tableId"):
        if k in result and isinstance(result[k], (int, float, bool, str)):
            print(f"  {k}: {result[k]}")


def _resolve_output_path(ts):
    """落到 <cwd>/linkfox/<date>/<session>/data/<slug>-<ts>.json。"""
    return resolve_data_path(SLUG, ts)


def _validate(params):
    if not isinstance(params, dict):
        return "参数必须是 JSON 对象"
    if not params.get("flowId"):
        # flowId 的格式由工作流侧定，所以只查非空，不查前缀
        return "缺少 flowId（工作流侧那条流的 id）"
    # tableId 必填但可为 None。用 `not in` 而不是 `.get() is None`：
    # 「显式传 null（解绑）」和「压根没传这个键」必须区分开 —— 后者是错，前者是正常用法。
    if "tableId" not in params:
        return (
            "缺少 tableId。这个参数**必填**：要换表就传 tbl 开头的 id，"
            "要解绑就显式传 null。不能用「省略字段」表达解绑 —— "
            "那样一次手滑就会静默停掉一条自动化。"
        )
    table_id = params["tableId"]
    if table_id is not None and (not isinstance(table_id, str) or not table_id.startswith("tbl")):
        return "tableId 必须是以 tbl 开头的字符串，或 null（解绑）"
    return None


def main():
    argv = sys.argv[1:]
    inline = "--inline" in argv
    argv = [a for a in argv if a != "--inline"]

    if not argv:
        print(
            f"Usage: smart_table.py updateWorkflowTriggerTable "
            '\'{"flowId":"your-flow-id","tableId":"tblXXX"}\' [--inline]\n'
            "  解绑（这条流不再被触发）：tableId 显式传 null",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        params = json.loads(argv[0])
    except json.JSONDecodeError as e:
        print(f"Invalid parameter format: {e}", file=sys.stderr)
        sys.exit(1)

    problem = _validate(params)
    if problem:
        print(problem, file=sys.stderr)
        sys.exit(1)

    result = call_api(params)

    serialized = json.dumps(result, ensure_ascii=False, indent=2)
    ts = int(time.time())
    out_path = _resolve_output_path(ts)
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(serialized)
        print(f"Saved full response: {out_path} ({len(serialized)} bytes)")
    except OSError as e:
        print(f"Failed to save to {out_path}: {e}", file=sys.stderr)

    if isinstance(result, dict) and result.get("errcode") != 200:
        hint = ""
        if result.get("errcode") == 403:
            hint = (
                "\n403 是**权限问题**（对那个多维表没有写权限，需拥有者/创建者/可编辑者），"
                "不是「找不到」。要如实这样告诉用户。"
            )
        elif result.get("errcode") == 400:
            hint = (
                "\n400 多半是新表不在这条流所属的多维表下面 —— 触发表只能选该流所属多维表里的表。"
            )
        print(
            f"Business error: errcode={result.get('errcode')} errmsg={result.get('errmsg')}{hint}",
            file=sys.stderr,
        )
    elif isinstance(result, dict):
        # errcode 200 不代表改动生效，还要看 status。把 not_found 当成功汇报是这条接口最容易犯的错。
        status = result.get("status")
        if status == "not_found":
            print(
                "⚠️ status=not_found：**什么都没改**。多维表这边没有这个 flowId 的关联。\n"
                "先用 smart_table.py listWorkflows 确认 flowId 抄对了，"
                "或者先用 smart_table.py registerWorkflow 登记关联。\n"
                "不要把这个结果汇报成「修改成功」。",
                file=sys.stderr,
            )
        elif status == "updated" and result.get("tableId") is None:
            print(
                "已解绑：这条流现在**没有触发表**，不会再被任何记录变化触发。"
                "要恢复的话，再调一次本技能传上新的 tableId。"
            )

    if inline or len(serialized.encode("utf-8")) <= SMALL_THRESHOLD:
        print(serialized)
    else:
        summarize(result)


if __name__ == "__main__":
    main()
