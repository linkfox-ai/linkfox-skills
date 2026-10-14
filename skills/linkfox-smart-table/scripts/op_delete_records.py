#!/usr/bin/env python3
"""智能表格-删除记录 - LinkFox Skill
调用 /smartTable/deleteRecords 接口。

⚠️ **不可逆**：物理硬删，回收站是唯一副本，接口本身不提供恢复。
⚠️ **全有全无**：只要有一个 recordId 查不到，整批失败、一条都不删。

必须先拿到用户明确确认再调。默认要求 `--yes`；缺它直接拒绝执行。

Usage:
  python smart_table.py deleteRecords '{"tableId":"tblXXX","recordIds":["recA","recB"]}' --yes
  python smart_table.py deleteRecords '<JSON>' --yes --inline
"""

import json
import os
import sys
import time
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API_PATH = "/smartTable/deleteRecords"
SLUG = "linkfox-smart-table-delete-records"

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
    """打印紧凑摘要。删除的响应很小，正常走不到这里。"""
    if not isinstance(result, dict):
        print(f"Response type: {type(result).__name__}")
        print(json.dumps(result, ensure_ascii=False)[:500])
        return
    print(f"Top-level keys: {list(result.keys())}")
    for k in ("errcode", "errmsg", "deleted"):
        if k in result and isinstance(result[k], (int, float, bool, str)):
            print(f"  {k}: {result[k]}")


def _resolve_output_path(ts):
    """落到 <cwd>/linkfox/<date>/<session>/data/<slug>-<ts>.json。"""
    return resolve_data_path(SLUG, ts)


def _validate(params):
    if not isinstance(params, dict):
        return "参数必须是 JSON 对象"
    if not params.get("tableId"):
        return "缺少 tableId（以 tbl 开头）"
    ids = params.get("recordIds")
    if not isinstance(ids, list) or not ids:
        return "缺少 recordIds（非空数组）"
    bad = [x for x in ids if not isinstance(x, str) or not x.startswith("rec")]
    if bad:
        return f"recordIds 里有不合法的 id（须以 rec 开头）：{bad[:5]}"
    if len(set(ids)) != len(ids):
        return "recordIds 里有重复项；去重后再调（全有全无语义下重复只会增加风险）"
    return None


def main():
    argv = sys.argv[1:]
    inline = "--inline" in argv
    confirmed = "--yes" in argv
    argv = [a for a in argv if a not in ("--inline", "--yes")]

    if not argv:
        print(
            f"Usage: smart_table.py deleteRecords "
            '\'{"tableId":"tblXXX","recordIds":["recXXX"]}\' --yes [--inline]',
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
        print(
            f"拒绝执行：删除不可逆（物理硬删、全有全无）。本次将删除 {len(params['recordIds'])} 条记录，"
            f"表 {params['tableId']}。\n"
            "先向用户复述要删的表和条数、拿到明确确认，再加 --yes 重跑。",
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
    # 失败时按"全有全无"解读：一条都没删，不要重试单条去凑。
    if isinstance(result, dict) and result.get("errcode") != 200:
        print(
            f"Business error: errcode={result.get('errcode')} errmsg={result.get('errmsg')}\n"
            "这个接口是全有全无的：失败意味着**一条都没删**。",
            file=sys.stderr,
        )

    if inline or len(serialized.encode("utf-8")) <= SMALL_THRESHOLD:
        print(serialized)
    else:
        summarize(result)


if __name__ == "__main__":
    main()
