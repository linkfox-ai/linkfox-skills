#!/usr/bin/env python3
"""智能表格-删列 - LinkFox Skill
调用 /smartTable/deleteFields 接口。

⚠️ **按不可恢复对待**：回收站里有快照，但恢复要的权限这套接口给不了。
⚠️ **全有全无**：任何一个列名查不到，整批失败、一列都不删。
⚠️ **删一列 = 没了每一行的那一格**，破坏范围比删行大一个量级。

必须先拿到用户明确确认再调。默认要求 `--yes`；缺它直接拒绝执行。

Usage:
  python smart_table.py deleteFields '{"tableId":"tblXXX","fieldNames":["备注"]}' --yes
  python smart_table.py deleteFields '{"tableId":"tblXXX","fieldNames":["价格"],"allowBreakingDependents":true}' --yes
"""

import json
import os
import sys
import time
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API_PATH = "/smartTable/deleteFields"
SLUG = "linkfox-smart-table-delete-fields"

# 响应 <= 该字节数时落盘后额外全量打印到 stdout；超过则只打摘要
SMALL_THRESHOLD = 8000

MAX_FIELDS = 50

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
    """删完之后的完整表头 + 被弄坏的列。"""
    if not isinstance(result, dict):
        print(f"Response type: {type(result).__name__}")
        print(json.dumps(result, ensure_ascii=False)[:500])
        return

    print(f"已删 {result.get('deleted')} 列")
    broken = result.get("brokenDependents") or []
    if broken:
        print(f"⚠️ 这些列已失效，需要到页面上修：{broken}")
    fields = result.get("fields") or []
    print(f"删完剩 {len(fields)} 个字段：")
    for field in fields:
        if not isinstance(field, dict):
            continue
        mark = "  [主字段]" if field.get("isPrimary") else ""
        print(f"  {field.get('name')}  ({field.get('type')}){mark}")


def _resolve_output_path(ts):
    """落到 <cwd>/linkfox/<date>/<session>/data/<slug>-<ts>.json。"""
    return resolve_data_path(SLUG, ts)


def _validate(params):
    if not isinstance(params, dict):
        return "参数必须是 JSON 对象"
    table_id = params.get("tableId")
    if not table_id:
        return "缺少 tableId（以 tbl 开头）"
    if not str(table_id).startswith("tbl"):
        return (
            f"tableId 必须以 tbl 开头，收到 {table_id!r}。"
            "用 smart_table.py listMyTables 按表名找到它。"
        )

    names = params.get("fieldNames")
    if not isinstance(names, list) or not names:
        return "缺少 fieldNames（非空数组，传**列名**不是 fldXXX）"
    if len(names) > MAX_FIELDS:
        return f"一次最多删 {MAX_FIELDS} 列，收到 {len(names)} 列；分批调用"

    bad = [x for x in names if not isinstance(x, str) or not x.strip()]
    if bad:
        return f"fieldNames 里有空值或非字符串：{bad[:5]}"

    # 传 fldXXX 是最可能的误用：别的表格 API 习惯用字段 id，而本接口只认列名。
    # 服务端会当成"这个列名不存在"报错，本地先说清楚原因。
    looks_like_id = [x for x in names if x.startswith("fld") and " " not in x and len(x) > 10]
    if looks_like_id:
        return (
            f"这些看起来是字段 id 而不是列名：{looks_like_id[:5]}。"
            "本接口按**列名**寻址，用 smart_table.py listFields 取列名。"
        )

    if len(set(names)) != len(names):
        return "fieldNames 里有重复项；去重后再调"
    return None


def main():
    argv = sys.argv[1:]
    inline = "--inline" in argv
    confirmed = "--yes" in argv
    argv = [a for a in argv if a not in ("--inline", "--yes")]

    if not argv:
        print(
            f"Usage: smart_table.py deleteFields "
            '\'{"tableId":"tblXXX","fieldNames":["备注"]}\' --yes [--inline]',
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

    if not confirmed:
        extra = ""
        if params.get("allowBreakingDependents"):
            extra = (
                "\n⚠️ 你还传了 allowBreakingDependents: true —— 这会连带弄坏引用这些列的"
                "公式/汇总/lookup 列。必须先把会失效的列名告诉用户并拿到确认。"
            )
        print(
            f"拒绝执行：删列按不可恢复对待，且删一列 = 没了每一行的那一格。"
            f"本次将删除 {len(params['fieldNames'])} 列（{params['fieldNames']}），"
            f"表 {params['tableId']}。{extra}\n"
            "先用 smart_table.py listFields 确认列名、向用户复述要删哪几列、"
            "拿到明确确认，再加 --yes 重跑。",
            file=sys.stderr,
        )
        sys.exit(2)

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

    # 业务失败不靠 HTTP 状态码判断，看 errcode。
    # 失败时按"全有全无"解读：一列都没删，不要拆成单列重试去凑。
    if isinstance(result, dict) and result.get("errcode") != 200:
        print(
            f"Business error: errcode={result.get('errcode')} errmsg={result.get('errmsg')}\n"
            "这个接口是全有全无的：失败意味着**一列都没删**。\n"
            "若报的是「有列依赖你要删的列」：先把会失效的列名告诉用户、拿到确认，"
            "再传 allowBreakingDependents: true 重来。不要自己直接加上重试。",
            file=sys.stderr,
        )
        print(serialized)
        return

    broken = result.get("brokenDependents") or [] if isinstance(result, dict) else []

    if inline or len(serialized.encode("utf-8")) <= SMALL_THRESHOLD:
        print(serialized)
        if broken:
            print(f"\n⚠️ 这些列已失效，需要到页面上修：{broken}")
    else:
        summarize(result)


if __name__ == "__main__":
    main()
