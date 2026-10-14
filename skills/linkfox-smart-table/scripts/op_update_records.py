#!/usr/bin/env python3
"""智能表格-更新记录 - LinkFox Skill
调用 /smartTable/updateRecords 接口。

批量改已有记录的单元格。字段按**名称**寻址；`typecast` 默认开（字符串会被自动转成字段类型）。
⚠️ 这条接口**只改已有记录，不能新增行**；改动**不进前端撤销栈**。

Usage:
  python smart_table.py updateRecords '{"tableId":"tblXXX","records":[{"recordId":"recXXX","fields":{"标题":"新值"}}]}'
  python smart_table.py updateRecords '<JSON>' --inline
"""

import json
import os
import sys
import time
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API_PATH = "/smartTable/updateRecords"
SLUG = "linkfox-smart-table-update-records"

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


def _find_main_list(obj):
    """递归找到元素数最多的 list 字段。不写死字段名，适配任意结构。"""
    best = (None, None, -1)

    def walk(node, path):
        nonlocal best
        if isinstance(node, list):
            if len(node) > best[2]:
                best = (path, node, len(node))
        elif isinstance(node, dict):
            for k, v in node.items():
                walk(v, f"{path}.{k}" if path else k)

    walk(obj, "")
    return best[0], best[1]


def summarize(result):
    """打印紧凑摘要：顶层字段 + 常见计数 + 最大列表前 3 条。"""
    if not isinstance(result, dict):
        print(f"Response type: {type(result).__name__}")
        print(json.dumps(result, ensure_ascii=False)[:500])
        return

    print(f"Top-level keys: {list(result.keys())}")
    for k in ("errcode", "errmsg", "updated"):
        if k in result and isinstance(result[k], (int, float, bool, str)):
            print(f"  {k}: {result[k]}")

    list_path, main_list = _find_main_list(result)
    if list_path is not None and main_list:
        sample = main_list[:3]
        print(f"\nMain list field: `{list_path}` (length={len(main_list)})")
        print(f"Sample (first {len(sample)} of {len(main_list)}):")
        print(json.dumps(sample, indent=2, ensure_ascii=False))
        print("\n提示：返回的是更新**后**的值。开了 typecast 时以这里为准，别假设写进去的就是原样。")


def _resolve_output_path(ts):
    """落到 <cwd>/linkfox/<date>/<session>/data/<slug>-<ts>.json。"""
    return resolve_data_path(SLUG, ts)


def _validate(params):
    """本地预检：把明显的入参错误在发请求前挡掉，省一次往返。"""
    if not isinstance(params, dict):
        return "参数必须是 JSON 对象"
    if not params.get("tableId"):
        return "缺少 tableId（以 tbl 开头）"
    records = params.get("records")
    if not isinstance(records, list) or not records:
        return "缺少 records（非空数组）"
    for i, rec in enumerate(records):
        if not isinstance(rec, dict):
            return f"records[{i}] 必须是对象"
        if not rec.get("recordId"):
            return f"records[{i}] 缺少 recordId（以 rec 开头）；这个接口不能新增行"
        if not isinstance(rec.get("fields"), dict) or not rec["fields"]:
            return f"records[{i}] 的 fields 必须是非空对象，key 用**字段名**"
    return None


def main():
    argv = sys.argv[1:]
    inline = "--inline" in argv
    argv = [a for a in argv if a != "--inline"]

    if not argv:
        print(
            f"Usage: smart_table.py updateRecords "
            '\'{"tableId":"tblXXX","records":[{"recordId":"recXXX","fields":{"字段名":"值"}}]}\' [--inline]',
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
    if isinstance(result, dict):
        if result.get("errcode") != 200:
            # 整批在一个事务里，失败会整体回滚
            print(
                f"Business error: errcode={result.get('errcode')} errmsg={result.get('errmsg')}\n"
                "整批是一个事务：失败意味着**一条都没改**，改完入参可整批重跑。",
                file=sys.stderr,
            )
        else:
            # 200 不等于全改到了：recordId 已不存在的会被静默跳过
            asked = len(params["records"])
            updated = result.get("updated")
            if isinstance(updated, int) and updated != asked:
                print(
                    f"⚠️ 只更新了 {updated}/{asked} 条。差额是**已不存在的 recordId**（被静默跳过）。"
                    "用 listRecords 查清那几条的状态，别把 200 当成全部改好。",
                    file=sys.stderr,
                )

    if inline or len(serialized.encode("utf-8")) <= SMALL_THRESHOLD:
        print(serialized)
    else:
        summarize(result)


if __name__ == "__main__":
    main()
