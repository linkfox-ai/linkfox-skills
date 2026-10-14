#!/usr/bin/env python3
"""智能表格-读取表结构 - LinkFox Skill
调用 /smartTable/listFields 接口。

读一张表有哪些列（字段 id + 字段名 + 类型 + 单选可选项 + 哪些是算出来的写不进去）。
**往表里写数据之前先调这个** —— 字段名写错时写入接口是整批拒绝的。

⚠️ `fieldId`（`fldXXX`）**不是写入用的**：写入一律按字段名。它只在配工作流触发条件时用得上。

Usage:
  python smart_table.py listFields '{"tableId":"tblXXX"}'
  python smart_table.py listFields '{"tableId":"tblXXX","includeChoices":false}'
  python smart_table.py listFields '{"tableId":"tblXXX"}' --inline
"""

import json
import os
import sys
import time
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API_PATH = "/smartTable/listFields"
SLUG = "linkfox-smart-table-list-fields"

# 响应 <= 该字节数时落盘后额外全量打印到 stdout；超过则只打摘要
SMALL_THRESHOLD = 8000

# 服务端会给 isComputed 标记，所以这里不自己维护一份"哪些类型算出来的"清单 —— 那种表会漂移。

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
    """一行一个字段的紧凑清单 + 写入时要注意的那几类单独点出来。"""
    if not isinstance(result, dict):
        print(f"Response type: {type(result).__name__}")
        print(json.dumps(result, ensure_ascii=False)[:500])
        return

    fields = result.get("fields") or []
    print(f"表：{result.get('name')}  ({result.get('tableId')})  共 {result.get('total')} 个字段")
    print()
    for field in fields:
        if not isinstance(field, dict):
            continue
        marks = []
        if field.get("isPrimary"):
            marks.append("主字段")
        if field.get("isComputed"):
            marks.append("算出来的·写不进去")
        if field.get("isMultipleCellValue"):
            marks.append("多值·传数组")
        suffix = f"  [{' / '.join(marks)}]" if marks else ""
        line = f"  {field.get('name')}  ({field.get('type')}){suffix}"
        if field.get("max") is not None:
            line += f"  max={field['max']}"
        # 摘要模式（宽表）走的是这条路，全量 JSON 不会打印 —— fieldId 不带上，
        # 配工作流触发条件时就只能再调一次接口。
        if field.get("fieldId"):
            line += f"  id={field['fieldId']}"
        print(line)
        if field.get("choices"):
            print(f"      可选项: {field['choices']}")
        if field.get("description"):
            print(f"      说明: {field['description']}")

    writable = [f.get("name") for f in fields if isinstance(f, dict) and not f.get("isComputed")]
    computed = [f.get("name") for f in fields if isinstance(f, dict) and f.get("isComputed")]
    if computed:
        print(f"\n⚠️ 这些字段写不进去（算出来的）：{computed}")
    print(f"\n可写入的字段名：{writable}")


def _resolve_output_path(ts):
    """落到 <cwd>/linkfox/<date>/<session>/data/<slug>-<ts>.json。"""
    return resolve_data_path(SLUG, ts)


def main():
    argv = sys.argv[1:]
    inline = "--inline" in argv
    argv = [a for a in argv if a != "--inline"]

    if not argv:
        print(
            f"Usage: smart_table.py listFields '{{\"tableId\":\"tblXXX\"}}' [--inline]",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        params = json.loads(argv[0])
    except json.JSONDecodeError as e:
        print(f"Invalid parameter format: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(params, dict) or not params.get("tableId"):
        print("Missing required parameter: tableId (以 tbl 开头)", file=sys.stderr)
        sys.exit(1)

    if not str(params["tableId"]).startswith("tbl"):
        print(
            f"tableId 必须以 tbl 开头，收到 {params['tableId']!r}。"
            "用 smart_table.py listMyTables 按表名找到它。",
            file=sys.stderr,
        )
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
        print(serialized)
        return

    if inline or len(serialized.encode("utf-8")) <= SMALL_THRESHOLD:
        print(serialized)
        # 全量打印时也给一份"哪些能写"的结论，省得调用方自己筛 isComputed
        fields = result.get("fields") or []
        computed = [f.get("name") for f in fields if isinstance(f, dict) and f.get("isComputed")]
        if computed:
            print(f"\n⚠️ 这些字段写不进去（算出来的）：{computed}")
    else:
        summarize(result)


if __name__ == "__main__":
    main()
