#!/usr/bin/env python3
"""智能表格-查 AI 出图进度 - LinkFox Skill
调用 /smartTable/getAiFillStatus 接口。

查 fillAiField 返回的 taskId 跑到哪了：完成 / 失败 / 进行中各多少行，失败的行和原因
（最常见：提示词引用的列为空，或参考图用不了）。只读。

Usage:
  python smart_table.py getAiFillStatus '{"tableId":"tblXXX","taskId":"tskXXX"}'
  python smart_table.py getAiFillStatus '<JSON>' --inline
"""

import json
import os
import sys
import time
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API_PATH = "/smartTable/getAiFillStatus"
SLUG = "linkfox-smart-table-get-ai-fill-status"

# 响应 <= 该字节数时落盘后额外全量打印到 stdout；超过则只打摘要
SMALL_THRESHOLD = 8000

# linkfox_paths.py 由 scaffold 从 linkfoxagent-v2/_shared 复制到本目录 scripts/，原样不改。
from linkfox_paths import get_api_base, resolve_data_path

DONE_STATUSES = ("completed", "failed", "cancelled")


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
    """失败行很多时才会走到这里：打计数 + 前 10 条失败。"""
    if not isinstance(result, dict):
        print(json.dumps(result, ensure_ascii=False)[:500])
        return
    for k in ("errcode", "errmsg", "taskId", "status", "total", "completed", "failed", "running", "pending"):
        if k in result:
            print(f"  {k}: {result[k]}")
    for row in (result.get("failures") or [])[:10]:
        print(f"  - {row.get('recordId')}: {row.get('error')}")


def _resolve_output_path(ts):
    """落到 <cwd>/linkfox/<date>/<session>/data/<slug>-<ts>.json。"""
    return resolve_data_path(SLUG, ts)


def _validate(params):
    if not isinstance(params, dict):
        return "参数必须是 JSON 对象"
    table_id = params.get("tableId")
    if not table_id or not str(table_id).startswith("tbl"):
        return "缺少 tableId（以 tbl 开头）—— 必须是触发 fillAiField 时的那张表"
    task_id = params.get("taskId")
    if not task_id or not str(task_id).startswith("tsk"):
        return "缺少 taskId（以 tsk 开头，取自 fillAiField 的出参）"
    return None


def main():
    argv = sys.argv[1:]
    inline = "--inline" in argv
    argv = [a for a in argv if a != "--inline"]

    if not argv:
        print(
            "Usage: smart_table.py getAiFillStatus "
            '\'{"tableId":"tblXXX","taskId":"tskXXX"}\' [--inline]',
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
        print(
            f"Business error: errcode={result.get('errcode')} errmsg={result.get('errmsg')}",
            file=sys.stderr,
        )
    elif isinstance(result, dict):
        status = result.get("status")
        if status not in DONE_STATUSES:
            print(
                f"还在生成：完成 {result.get('completed')}/{result.get('total')}，"
                f"进行中 {result.get('running')}，排队 {result.get('pending')}。一行最长约 10 分钟，过一会儿再查。"
            )
        elif result.get("failed"):
            print(
                f"已结束（{status}）：成功 {result.get('completed')} 行，失败 {result.get('failed')} 行。"
                "失败原因见 failures；成功的图用 listRecords 取。"
            )
        else:
            print(f"已结束（{status}）：{result.get('completed')} 行全部完成。用 listRecords 取图。")

    if inline or len(serialized.encode("utf-8")) <= SMALL_THRESHOLD:
        print(serialized)
    else:
        summarize(result)


if __name__ == "__main__":
    main()
