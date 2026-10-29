#!/usr/bin/env python3
"""智能表格-触发 AI 出图 - LinkFox Skill
调用 /smartTable/fillAiField 接口。

对一个**已配置 AI 出图的附件列**显式触发生成：建任务、入队，立刻返回 taskId；
图是异步生成的（一行最长约 10 分钟），用 getAiFillStatus 查进度，完成后用 listRecords 取图。

⚠️ 会扣**调用方自己**的积分。默认 mode=emptyOnly（只填还没有图的行）；mode=all 会**整格覆盖**已有的图。
⚠️ 按**单元格**去重：只有这一格已经在生成才跳过（skipped），其余格子照常入队；格子跑完就能重跑。
   被跳过的格子在 runningTaskIds 那几个任务里，进度要去查它们。

Usage:
  python smart_table.py fillAiField '{"tableId":"tblXXX","fieldName":"AI 场景图"}'
  python smart_table.py fillAiField '{"tableId":"tblXXX","fieldName":"AI 场景图","recordIds":["recA","recB"]}'
  python smart_table.py fillAiField '<JSON>' --inline
"""

import json
import os
import sys
import time
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API_PATH = "/smartTable/fillAiField"
SLUG = "linkfox-smart-table-fill-ai-field"

# 响应 <= 该字节数时落盘后额外全量打印到 stdout；超过则只打摘要
SMALL_THRESHOLD = 8000

# 与服务端 SMART_TABLE_AI_FILL_MAX_RECORD_IDS 一致。本地先拦，省一次往返
MAX_RECORD_IDS = 50

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
    """出参很小，正常走不到这里。"""
    print(json.dumps(result, ensure_ascii=False)[:800])


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
        return f"tableId 必须以 tbl 开头，收到 {table_id!r}。用 smart_table.py listMyTables 按表名找到它。"
    if not params.get("fieldName"):
        return "缺少 fieldName（已配置 AI 出图的附件列的列名）"
    record_ids = params.get("recordIds")
    if record_ids is not None:
        if not isinstance(record_ids, list) or not record_ids:
            return "recordIds 传了就必须是非空数组；要填整列就别传"
        if len(record_ids) > MAX_RECORD_IDS:
            return f"recordIds 单次最多 {MAX_RECORD_IDS} 行，收到 {len(record_ids)} 行；分批调用"
        bad = [r for r in record_ids if not isinstance(r, str) or not r.startswith("rec")]
        if bad:
            return f"recordIds 里有不是记录 id 的值（要以 rec 开头）：{bad[:5]}"
    mode = params.get("mode", "emptyOnly")
    if mode not in ("emptyOnly", "all"):
        return f"mode 只能是 emptyOnly（默认，只填空格）或 all（整格覆盖已有的图），收到 {mode!r}"
    return None


def main():
    argv = sys.argv[1:]
    inline = "--inline" in argv
    argv = [a for a in argv if a != "--inline"]

    if not argv:
        print(
            "Usage: smart_table.py fillAiField "
            '\'{"tableId":"tblXXX","fieldName":"AI 场景图"}\' [--inline]',
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
        running = result.get("runningTaskIds") or []
        skipped = result.get("skipped") or 0
        if result.get("reused") and "skipped" not in result:
            # 旧后端（还没按单元格去重）：这一列有任务在跑就整次不做，taskId 是那个在跑的任务
            print(
                f"这一列已经有一个没结束的生成任务（taskId={result.get('taskId')}），本次没有入队任何行。"
                "用 smart_table.py getAiFillStatus 查它的进度，结束后再调一次（emptyOnly 会接着填剩下的）。"
            )
        elif result.get("taskId") is None and skipped:
            print(
                f"这 {skipped} 格已经在生成中，本次没有新入队（不会重复扣费）。"
                f"它们在任务 {', '.join(running)} 里，用 smart_table.py getAiFillStatus 逐个查进度，"
                "全部结束后再 listRecords 取图。"
            )
        elif result.get("taskId") is None:
            if params.get("recordIds"):
                print("没有要生成的行：这几行已经有图了。要重新生成用 mode=all（会整格覆盖）。")
            else:
                # 整列 emptyOnly 时 rowCount 是「空格行数」，为 0 既可能是都有图了，也可能是表里没有行
                print(
                    "没有要生成的行：这一列要么已经都有图了，要么表里还没有行（先 createRecords）。"
                    "要重新生成已有的图用 mode=all（会整格覆盖）。"
                )
        else:
            print(
                f"已入队 {result.get('processedCount')} 行，taskId={result.get('taskId')}。图是异步生成的，"
                "用 smart_table.py getAiFillStatus 查进度，完成后用 listRecords 取图。"
            )
            if skipped:
                print(
                    f"另有 {skipped} 格已经在生成中、本次跳过（不会重复扣费），"
                    f"它们在任务 {', '.join(running)} 里——这几个任务的进度也要查，"
                    "都结束了才算整批完成，别只看本次的 taskId 就去取图。"
                )
            if result.get("isLimited"):
                print(
                    f"注意：符合条件的有 {result.get('rowCount')} 行，单次只入队了一部分。"
                    "等这次跑完再调一次（emptyOnly 会接着填剩下的）。"
                )

    if inline or len(serialized.encode("utf-8")) <= SMALL_THRESHOLD:
        print(serialized)
    else:
        summarize(result)


if __name__ == "__main__":
    main()
