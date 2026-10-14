#!/usr/bin/env python3
"""智能表格-查询工作流关联 - LinkFox Skill
调用 /smartTable/listWorkflows 接口。

列出「哪条流挂在哪个多维表下、由哪张数据表触发」。只读。

⚠️ 出参**不含流的名字** —— 名字在工作流侧，这里只给 flowId。
⚠️ tableId 为 null 的流不会被任何记录变化触发。

Usage:
  python smart_table.py listWorkflows
  python smart_table.py listWorkflows '{"notebookId":"nbkXXX"}'
  python smart_table.py listWorkflows '{}' --inline
"""

import json
import os
import sys
import time
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API_PATH = "/smartTable/listWorkflows"
SLUG = "linkfox-smart-table-list-workflows"

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
    """打印紧凑摘要。不分页 + 十几条的量级，正常走不到这里。"""
    if not isinstance(result, dict):
        print(f"Response type: {type(result).__name__}")
        print(json.dumps(result, ensure_ascii=False)[:500])
        return
    print(f"Top-level keys: {list(result.keys())}")
    for k in ("errcode", "errmsg", "total"):
        if k in result and isinstance(result[k], (int, float, bool, str)):
            print(f"  {k}: {result[k]}")
    rows = result.get("workflows")
    if isinstance(rows, list):
        for row in rows[:20]:
            if isinstance(row, dict):
                trigger = row.get("tableId") or "<未设置触发表，不会被触发>"
                print(f"  - flowId={row.get('flowId')} notebook={row.get('notebookId')} 触发表={trigger}")
        if len(rows) > 20:
            print(f"  ...（共 {len(rows)} 条，完整内容见落盘文件）")


def _resolve_output_path(ts):
    """落到 <cwd>/linkfox/<date>/<session>/data/<slug>-<ts>.json。"""
    return resolve_data_path(SLUG, ts)


def _validate(params):
    if not isinstance(params, dict):
        return "参数必须是 JSON 对象"
    notebook_id = params.get("notebookId")
    if notebook_id is None:
        return None
    if not isinstance(notebook_id, str) or not notebook_id:
        return "notebookId 必须是非空字符串（多维表 id，以 nbk 开头），或整个省略"
    # 传数据表 id 会得到空列表而不是报错，很容易被误读成「这个多维表下没有自动化」。
    if notebook_id.startswith("tbl"):
        return (
            "notebookId 传的是数据表 id（tbl 开头）。这里要的是**多维表**id："
            "取列表接口顶层的 notebooks[].notebookId，不是里面的 tables[].tableId。"
            "（服务端对这种入参回的是空列表而不是报错，所以本地拦下来。）"
        )
    return None


def main():
    argv = sys.argv[1:]
    inline = "--inline" in argv
    argv = [a for a in argv if a != "--inline"]

    # 参数整个可省：等价于 {}，列出自己能看到的全部
    if not argv:
        params = {}
    else:
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
        print(
            f"Business error: errcode={result.get('errcode')} errmsg={result.get('errmsg')}",
            file=sys.stderr,
        )
    elif isinstance(result, dict):
        rows = result.get("workflows") or []
        if not rows:
            # 空列表是成功，但成因有两种，别让调用方只报「没有自动化」
            print(
                "空结果。两种可能：确实没有登记过任何工作流关联；"
                "或者那些多维表当前身份看不见（可见性过滤与侧栏同一口径，看不见的不会出现在这里）。"
            )
        else:
            no_trigger = [r.get("flowId") for r in rows if isinstance(r, dict) and r.get("tableId") is None]
            if no_trigger:
                print(
                    f"注意：{len(no_trigger)} 条流**没有设置触发表**，不会被任何记录变化触发："
                    f"{no_trigger[:10]}。成因是登记时还没配触发器，或原表被删后后端自动置空了。"
                )

    if inline or len(serialized.encode("utf-8")) <= SMALL_THRESHOLD:
        print(serialized)
    else:
        summarize(result)


if __name__ == "__main__":
    main()
