#!/usr/bin/env python3
"""智能表格-重命名多维表 - LinkFox Skill
调用 /smartTable/renameNotebook 接口。

⚠️ **只改多维表（容器）自己的名字**：里面数据表的名字不跟着变，反过来改数据表名也不会动多维表名。
   createTable 建出来时两者同名，用户常以为是一个东西 —— 用户说「把这个表改成 X」时先问清改哪一个，
   两个都要改就分别调 renameNotebook 和 renameTable。
⚠️ **权限**：只有多维表的创建者能改；协作者（「可编辑」「可查看」）一律 404。
⚠️ **同一创建者名下不能重名**：已有同名多维表（**包括回收站里的**，它们的名字还占着）→ 400，什么都没改。
   把冲突告诉用户、请他换个名字；**不要自己加后缀重试**。
⚠️ **只改名字**：图标、里面的列名都改不了（列名这套接口做不到，只能在页面上改）。

改名可逆，不设 `--yes` 闸门（同 updateRecords）。但一律按 notebookId 改：先 listMyTables 按名字找到它，
同名多个就让用户挑，别猜。改成原名直接回成功，所以超时后用同样的参数重试是安全的。

Usage:
  python smart_table.py renameNotebook '{"notebookId":"nbkXXX","name":"新名字"}'
"""

import json
import os
import socket
import sys
import time
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API_PATH = "/smartTable/renameNotebook"
SLUG = "linkfox-smart-table-rename-notebook"

# 响应 <= 该字节数时落盘后额外全量打印到 stdout；超过则只打摘要
SMALL_THRESHOLD = 8000

TIMEOUT_SECONDS = 120

ALLOWED_KEYS = {"notebookId", "name"}

# 服务端规则：trim 后 1–255 字。按 JS 的口径算（trim 的空白集合、UTF-16 长度），本地预检才与服务端一致
MAX_NAME_LENGTH = 255
_JS_WHITESPACE = "".join(map(chr, (
    0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x20, 0xA0, 0x1680, *range(0x2000, 0x200B),
    0x2028, 0x2029, 0x202F, 0x205F, 0x3000, 0xFEFF,
)))

# 照着别的接口 / 口语写歪的「新名字」参数名
NAME_ALIASES = ("newName", "title", "notebookName", "tableName", "itemName", "label")

# 这几种结果说不准改没改：超时 / 连不上 / 网关超时 / 服务端异常。
# 改名是幂等的（改成原名直接回成功），原样重试不会出事
UNCERTAIN_ERRCODES = {0, 500, 502, 503, 504}

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


def _timeout_result():
    return {
        "errcode": 0,
        "errmsg": f"等待超时（{TIMEOUT_SECONDS} 秒）。**说不准改没改**，不代表失败，也不代表改好了",
    }


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
        with urlopen(req, timeout=TIMEOUT_SECONDS) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        try:
            return json.loads(body) if body else {"errcode": e.code, "errmsg": f"HTTP {e.code}: {e.reason}"}
        except Exception:
            return {"errcode": e.code, "errmsg": f"HTTP {e.code}: {e.reason}", "details": body}
    except (socket.timeout, TimeoutError):
        # 读超时在不同 Python 版本里不一定包成 URLError，单独接住
        return _timeout_result()
    except URLError as e:
        if isinstance(e.reason, (socket.timeout, TimeoutError)):
            return _timeout_result()
        return {"errcode": 0, "errmsg": f"Connection failed: {e.reason}"}


def _payload(result):
    """业务字段。内网信封是平铺的（与其余操作一致）；万一网关把它包进 data，也认。"""
    if isinstance(result, dict) and isinstance(result.get("data"), dict):
        return result["data"]
    return result if isinstance(result, dict) else {}


def summarize(result):
    """打印紧凑摘要。改名的响应很小，正常走不到这里。"""
    if not isinstance(result, dict):
        print(f"Response type: {type(result).__name__}")
        print(json.dumps(result, ensure_ascii=False)[:500])
        return
    print(f"Top-level keys: {list(result.keys())}")
    payload = _payload(result)
    for k in ("errcode", "errmsg"):
        if k in result and isinstance(result[k], (int, float, bool, str)):
            print(f"  {k}: {result[k]}")
    for k in ("notebookId", "name"):
        if k in payload and isinstance(payload[k], (int, float, bool, str)):
            print(f"  {k}: {payload[k]}")


def _js_trim(value):
    return value.strip(_JS_WHITESPACE)


def _note_stored_name(name, requested_name):
    """回的名字和入参不一样时说清楚：跟用户说的是存下来的那个。"""
    if not isinstance(requested_name, str) or name is None or name == requested_name:
        return
    why = "首尾空白已去掉" if name == _js_trim(requested_name) else "与入参不同"
    print(f"服务端存下的名字是「{name}」（{why}），跟用户说这个，别照抄入参。")


def _report(payload, requested_name):
    """给 agent 的结论：改成了什么、怎么跟用户说。名字以服务端回的为准（它会 trim）。"""
    name = payload.get("name")
    print(f"已把多维表（{payload.get('notebookId')}）的名字改为「{name}」。")
    _note_stored_name(name, requested_name)
    print(
        "里面数据表的名字**没有跟着变**（两者各自独立）。用户要的如果是改表名，"
        "再用 renameTable 按 tableId 改。"
    )


def _resolve_output_path(ts):
    """落到 <cwd>/linkfox/<date>/<session>/data/<slug>-<ts>.json。"""
    return resolve_data_path(SLUG, ts)


# 拿错 id 是最可能的误用：手上有什么 id 就往里塞。按前缀说清它是什么、该走哪条
_WRONG_PREFIX_HINTS = {
    "tbl": (
        "这是数据表 id（tbl 开头），不是多维表 id。改这张数据表的名字 → 用 renameTable（传 tableId）；"
        "真要改它所在多维表的名字 → 先 smart_table.py listMyTables，在 notebooks[].tables[] 里找到这个 tableId，"
        "取它所在那一项的 notebookId 再来"
    ),
    "bnf": "这是文件夹 id（bnf 开头）。改文件夹名用 renameNotebookItem，itemType 传 \"folder\"",
    "pag": "这是页面 id（pag 开头）。改页面名用 renameNotebookItem，itemType 传 \"page\"",
    "apl": "这是应用 id（apl 开头）。改应用名用 renameNotebookItem，itemType 传 \"application\"",
    "dsh": "这是仪表盘 id（dsh 开头）。改仪表盘名用 renameNotebookItem，itemType 传 \"dashboard\"",
    "fld": "这是字段 id（fld 开头）。**列名这套接口改不了**，请用户在页面上改",
    "shr": "这是分享 id（shr 开头），不能拿来改名。用 listMyTables 找到多维表的 notebookId",
}


def _validate_name(params):
    """新名字：必填、字符串、trim 后 1–255 字（与服务端同一口径）。"""
    if "name" not in params:
        alias = next((k for k in NAME_ALIASES if k in params), None)
        if alias:
            return f"新名字的参数名是 name，不是 {alias}：把 {alias!r} 改成 \"name\""
        return "缺少 name（新名字）。用户没说改成什么就先问，别自己起名"
    name = params["name"]
    if not isinstance(name, str):
        return f"name 必须是字符串，收到 {name!r}"
    trimmed = _js_trim(name)
    if not trimmed:
        return "name 不能为空（去掉首尾空白后什么都不剩）。问用户要改成什么"
    length = len(trimmed.encode("utf-16-le")) // 2
    if length > MAX_NAME_LENGTH:
        note = "（emoji 等字符按 2 字算）" if length != len(trimmed) else ""
        return (
            f"name 太长：去掉首尾空白后 {length} 字{note}，最多 {MAX_NAME_LENGTH} 字。"
            "请用户给个短一点的，别自己截断"
        )
    return None


def _validate(params):
    if not isinstance(params, dict):
        return "参数必须是 JSON 对象"

    notebook_id = params.get("notebookId")
    if not notebook_id:
        if params.get("tableId"):
            return (
                "renameNotebook 改的是**多维表**的名字，要 notebookId（nbk 开头），不收 tableId。"
                "改数据表名 → 用 renameTable；真要改多维表名 → 用 listMyTables 查出它的 notebookId"
            )
        if params.get("itemId") or params.get("itemType"):
            return "改多维表里的仪表盘 / 文件夹 / 页面 / 应用的名字 → 用 renameNotebookItem，不是 renameNotebook"
        return (
            "缺少 notebookId（nbk 开头）。用 smart_table.py listMyTables 按名字找到 notebooks[].notebookId"
            "（只有自己创建的多维表能改名，listSharedTables 里的改不了）"
        )
    if not isinstance(notebook_id, str):
        return f"notebookId 必须是字符串，收到 {notebook_id!r}"
    if not notebook_id.startswith("nbk"):
        hint = _WRONG_PREFIX_HINTS.get(notebook_id[:3])
        return (
            f"notebookId 必须以 nbk 开头，收到 {notebook_id!r}。"
            + (hint or "用 smart_table.py listMyTables 查 notebooks[].notebookId")
        )

    # 想改列名的先拦（在查 name 之前）：服务端会静默丢掉这些字段、把多维表改成 name 那个名字
    field_keys = sorted({"fieldName", "fieldNames", "fieldId", "fields", "oldName"} & set(params))
    if field_keys:
        return (
            f"renameNotebook 改的是多维表的名字，不收 {field_keys}。"
            "**列名这套接口改不了**，请用户在页面上改；要改的是多维表名就去掉这些参数再调"
        )

    problem = _validate_name(params)
    if problem:
        return problem

    # 服务端会**静默丢弃**没声明的字段
    unknown = sorted(set(params) - ALLOWED_KEYS)
    if unknown:
        if "tableId" in unknown:
            return (
                "renameNotebook 只认 notebookId，tableId 会被静默丢掉、改的仍是**多维表**的名字。"
                "要改数据表名 → 用 renameTable；两个都要改就分别调"
            )
        if "icon" in unknown:
            return "这套接口**只能改名字**，图标改不了（请用户在页面上改）。去掉 icon 再调"
        return (
            f"renameNotebook 只收 notebookId、name，多了 {unknown}。"
            "服务端会静默丢掉它们 —— 去掉再调"
        )
    return None


def _hint(errcode, errmsg):
    """按错误码给一句「接下来怎么办」。errmsg 原文照样打印，这里只补方向。"""
    errmsg = errmsg or ""
    if errcode in UNCERTAIN_ERRCODES:
        return (
            "\n这种结果**说不准改没改**（超时 / 连不上 / 服务端异常），别跟用户说「改好了」，也别说「没改」。"
            "用**同样的** notebookId 和 name 原样重试是安全的：已经改成这个名字的再改一次只会回成功。"
            "也可以先 smart_table.py listMyTables 看名字变没变。"
        )
    head = "\n这次**名字没有改**。"
    if errcode == 400 and "already exists" in errmsg:
        return (
            head + "你名下已经有一个叫这个名字的多维表（**回收站里的也算**，它们的名字还占着）。"
            "把冲突告诉用户、请他换个名字；**不要自己加后缀或编号重试**。"
            "用户说「明明没有同名的」，多半是回收站里还有一个。"
        )
    if errcode == 400:
        return head + "多半是名字不合法（去掉首尾空白后要 1–255 字）或 notebookId 格式不对，按 errmsg 改。"
    if errcode == 404:
        return (
            head + "多维表不存在、不在你当前团队里、已进回收站，或者你不是它的创建者"
            "（只有创建者能改多维表名，「可编辑」「可查看」的协作者一律回 404）。"
            "用 listMyTables 核对 notebookId：只在 listSharedTables 里的是别人的多维表，请它的创建者来改。"
        )
    if errcode == 403:
        return head + "没有改这个多维表名字的权限（只有创建者能改）。告诉用户请多维表的创建者来改。"
    return head + "按 errmsg 原文改。"


def main():
    argv = sys.argv[1:]
    inline = "--inline" in argv
    # 改名不设确认闸门；顺手带了 --yes 的也认，不当成 JSON 参数
    argv = [a for a in argv if a not in ("--inline", "--yes")]

    if not argv:
        print(
            "Usage: smart_table.py renameNotebook "
            '\'{"notebookId":"nbkXXX","name":"新名字"}\' [--inline]',
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
    errcode = result.get("errcode") if isinstance(result, dict) else None
    if errcode != 200:
        errmsg = result.get("errmsg") if isinstance(result, dict) else None
        print(
            f"Business error: errcode={errcode} errmsg={errmsg}{_hint(errcode, errmsg)}",
            file=sys.stderr,
        )
        print(serialized)
        return

    if inline or len(serialized.encode("utf-8")) <= SMALL_THRESHOLD:
        print(serialized)
    else:
        summarize(result)
    print()
    _report(_payload(result), params.get("name"))


if __name__ == "__main__":
    main()
