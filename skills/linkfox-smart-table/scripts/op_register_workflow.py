#!/usr/bin/env python3
"""智能表格-登记工作流关联 - LinkFox Skill
调用 /smartTable/registerWorkflow 接口。

把一条**已经存在**的工作流登记到某个多维表下面。不创建工作流本身。

幂等：同一个 flowId 重复登记不会建出第二条，直接回现状 + alreadyRegistered=true。
⚠️ 但重试**不会改 tableId** —— 改触发表要用 update-workflow-trigger-table。

Usage:
  python smart_table.py registerWorkflow '{"notebookId":"nbkXXX","flowId":"your-flow-id"}'
  python smart_table.py registerWorkflow '{"notebookId":"nbkXXX","flowId":"f1","tableId":"tblXXX"}' --inline
"""

import json
import os
import sys
import time
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API_PATH = "/smartTable/registerWorkflow"
SLUG = "linkfox-smart-table-register-workflow"

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
    for k in ("errcode", "errmsg", "flowId", "notebookId", "tableId", "alreadyRegistered"):
        if k in result and isinstance(result[k], (int, float, bool, str)):
            print(f"  {k}: {result[k]}")


def _resolve_output_path(ts):
    """落到 <cwd>/linkfox/<date>/<session>/data/<slug>-<ts>.json。"""
    return resolve_data_path(SLUG, ts)


def _validate(params):
    if not isinstance(params, dict):
        return "参数必须是 JSON 对象"
    notebook_id = params.get("notebookId")
    if not notebook_id:
        return "缺少 notebookId（多维表 id，以 nbk 开头）"
    # 最常见的错法：把数据表 id 当成多维表 id 传。服务端只会回一个 404，本地拦住能说清原因。
    if isinstance(notebook_id, str) and notebook_id.startswith("tbl"):
        return (
            "notebookId 传的是数据表 id（tbl 开头）。这里要的是**多维表**id："
            "取列表接口顶层的 notebooks[].notebookId，不是里面的 tables[].tableId"
        )
    if not params.get("flowId"):
        # flowId 的格式由工作流侧定，所以只查非空，不查前缀
        return "缺少 flowId（工作流侧那条流的 id）"
    table_id = params.get("tableId")
    if table_id is not None and (not isinstance(table_id, str) or not table_id.startswith("tbl")):
        return "tableId 必须是以 tbl 开头的字符串，或 null（表示还没设置触发表）"
    return None


def main():
    argv = sys.argv[1:]
    inline = "--inline" in argv
    argv = [a for a in argv if a != "--inline"]

    if not argv:
        print(
            f"Usage: smart_table.py registerWorkflow "
            '\'{"notebookId":"nbkXXX","flowId":"your-flow-id","tableId":"tblXXX"}\' [--inline]',
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

    # 业务失败不靠 HTTP 状态码判断，看 errcode
    if isinstance(result, dict) and result.get("errcode") != 200:
        hint = ""
        if result.get("errcode") == 404:
            hint = (
                "\n404 有三种成因且接口刻意不区分：多维表不存在 / 不在你团队 / 你对它没有写权限。"
                "核对 notebookId 是否取自列表接口顶层，以及当前身份对该多维表是否为"
                "拥有者/创建者/可编辑者之一。"
            )
        print(
            f"Business error: errcode={result.get('errcode')} errmsg={result.get('errmsg')}{hint}",
            file=sys.stderr,
        )
    elif isinstance(result, dict):
        # 这两句要显式说出来：不说的话，调用方很容易把「本来就有」当成「我刚建的」，
        # 或者不知道这条流其实还不会被触发。
        if result.get("alreadyRegistered"):
            print(
                "注意：这个 flowId **之前就已经登记过**，本次是幂等返回现状（没有新建）。"
                "而且 tableId 不会被本次调用改动 —— 要换触发表请用 "
                "smart_table.py updateWorkflowTriggerTable。"
            )
        if result.get("tableId") is None:
            print(
                "注意：这条流**没有设置触发表**，所以不会被任何记录变化触发。"
                "用 smart_table.py updateWorkflowTriggerTable 设置一张。"
            )

    if inline or len(serialized.encode("utf-8")) <= SMALL_THRESHOLD:
        print(serialized)
    else:
        summarize(result)


if __name__ == "__main__":
    main()
