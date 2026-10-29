#!/usr/bin/env python3
"""智能表格-重命名多维表里的仪表盘 / 文件夹 / 页面 / 应用 - LinkFox Skill
调用 /smartTable/renameNotebookItem 接口。

itemType 四选一：dashboard / folder / page / application；itemId 从 listMyTables / listSharedTables
里那个多维表的 dashboards / folders / pages / applications 数组拿，itemType 就是它所在的那个数组。
「页面」指多维表侧栏里的页面节点，与 linkfox-smart-table-page 技能（生成页面）不是一回事。

⚠️ **权限**：所在多维表的创建者，或「可编辑」的协作者；「可查看」的一律 404。
⚠️ **文件夹在同一个多维表里不能重名** → 400，什么都没改：把冲突告诉用户、请他换个名字，**不要自己加后缀重试**。
   仪表盘 / 页面 / 应用允许重名 —— 所以一律按 itemId 改，别按名字找了就改。
⚠️ **回收站里的、不在任何多维表里的** 一律 404。
⚠️ **只改名字**：内容、图标都不动；改文件夹名不影响里面的表和内容。

改名可逆，不设 `--yes` 闸门（同 updateRecords）。同名多个就让用户挑，别猜。
改成原名直接回成功，所以超时后用同样的参数重试是安全的。

Usage:
  python smart_table.py renameNotebookItem '{"itemType":"dashboard","itemId":"dshXXX","name":"新名字"}'
  python smart_table.py renameNotebookItem '{"itemType":"folder","itemId":"bnfXXX","name":"新名字"}'
"""

import json
import os
import socket
import sys
import time
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API_PATH = "/smartTable/renameNotebookItem"
SLUG = "linkfox-smart-table-rename-notebook-item"

# 响应 <= 该字节数时落盘后额外全量打印到 stdout；超过则只打摘要
SMALL_THRESHOLD = 8000

TIMEOUT_SECONDS = 120

ALLOWED_KEYS = {"itemType", "itemId", "name"}

# itemType → (给人看的名字, 列表出参里的数组名, id 前缀)。
# 仪表盘不卡前缀：存量仪表盘的 id 是 cuid，没有 dsh 前缀
ITEM_TYPES = {
    "dashboard": ("仪表盘", "dashboards", None),
    "folder": ("文件夹", "folders", "bnf"),
    "page": ("页面", "pages", "pag"),
    "application": ("应用", "applications", "apl"),
}

# 照着页面/口语写歪的 itemType → 正确写法
ITEM_TYPE_ALIASES = {
    "dashboards": "dashboard",
    "folders": "folder",
    "pages": "page",
    "applications": "application",
    "app": "application",
    "apps": "application",
}

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
    for k in ("itemType", "itemId", "name", "notebookId"):
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
    item_type = payload.get("itemType")
    label = ITEM_TYPES[item_type][0] if item_type in ITEM_TYPES else (item_type or "对象")
    name = payload.get("name")
    print(
        f"已把{label}（{payload.get('itemId')}，所在多维表 {payload.get('notebookId')}）"
        f"的名字改为「{name}」。"
    )
    _note_stored_name(name, requested_name)
    if item_type == "folder":
        print("只改了文件夹的名字，里面的数据表和内容原样不动。")


def _resolve_output_path(ts):
    """落到 <cwd>/linkfox/<date>/<session>/data/<slug>-<ts>.json。"""
    return resolve_data_path(SLUG, ts)


# id 前缀 → 它其实是哪种 itemType（用来在 itemType 与 itemId 对不上时给出准确的改法）
_TYPE_BY_PREFIX = {"bnf": "folder", "pag": "page", "apl": "application", "dsh": "dashboard"}

# 走的根本不是这条接口的 id：说清楚比报「itemType 不对」有用
_OTHER_OP_PREFIX_HINTS = {
    "tbl": "是数据表 id（tbl 开头）。改数据表名用 renameTable（传 tableId）",
    "nbk": "是多维表 id（nbk 开头）。改多维表名用 renameNotebook（传 notebookId）",
    "fld": "是字段 id（fld 开头）。**列名这套接口改不了**，请用户在页面上改",
}


def _validate_item_type(item_type):
    if not item_type:
        return (
            "缺少 itemType：dashboard / folder / page / application 四选一，"
            "看 itemId 出现在 listMyTables 里那个多维表的哪个数组（dashboards / folders / pages / applications）"
        )
    if not isinstance(item_type, str):
        return f"itemType 必须是字符串，收到 {item_type!r}"
    if item_type in ITEM_TYPES:
        return None
    lowered = item_type.strip().lower()
    if lowered in ("table", "tables", "datatable"):
        return "改数据表名用 renameTable（传 tableId），不是 renameNotebookItem"
    if lowered in ("notebook", "notebooks", "base"):
        return "改多维表名用 renameNotebook（传 notebookId），不是 renameNotebookItem"
    if lowered in ("field", "fields", "column", "columns"):
        return "**列名这套接口改不了**，请用户在页面上改"
    if lowered in ("workflow", "workflows", "automation"):
        return "工作流（自动化）的名字不在这里改：让用户到工作流侧改"
    fixed = ITEM_TYPE_ALIASES.get(lowered) or (lowered if lowered in ITEM_TYPES else None)
    if fixed:
        return f"itemType 写成了 {item_type!r}，应为 {fixed!r}（单数、全小写）"
    return f"itemType 只能是 dashboard / folder / page / application，收到 {item_type!r}"


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

    item_id = params.get("itemId")
    if not item_id:
        if params.get("itemIds"):
            return "一次只改一个对象，没有批量：itemIds 改成 itemId，逐个调"
        if params.get("tableId"):
            return "改数据表名用 renameTable（传 tableId），不是 renameNotebookItem"
        if params.get("notebookId"):
            return (
                "renameNotebookItem 要 itemType + itemId，不收 notebookId。"
                "要改多维表自己的名字 → 用 renameNotebook；改其中的仪表盘 / 文件夹 / 页面 / 应用 → "
                "从 listMyTables 里那个多维表的 dashboards / folders / pages / applications 拿 itemId"
            )
        return (
            "缺少 itemId。从 smart_table.py listMyTables（找不到再 listSharedTables）里那个多维表的 "
            "dashboards / folders / pages / applications 数组拿；同名多个就列给用户挑"
        )
    if not isinstance(item_id, str):
        return f"itemId 必须是字符串，收到 {item_id!r}"
    if len(item_id) > 64:
        return f"itemId 太长（{len(item_id)} 字），不像是列表里拿到的 id"

    other_op = _OTHER_OP_PREFIX_HINTS.get(item_id[:3])
    if other_op:
        return f"itemId={item_id!r} {other_op}"

    problem = _validate_item_type(params.get("itemType"))
    if problem:
        return problem
    item_type = params["itemType"]
    label, _, prefix = ITEM_TYPES[item_type]

    actual_type = _TYPE_BY_PREFIX.get(item_id[:3])
    if actual_type and actual_type != item_type:
        actual_label = ITEM_TYPES[actual_type][0]
        return (
            f"itemType={item_type!r} 与 itemId={item_id!r} 对不上：{item_id[:3]} 开头的是{actual_label}，"
            f"itemType 应传 {actual_type!r}。以 itemId 出现在列表里的哪个数组为准"
        )
    if prefix and not item_id.startswith(prefix):
        return f"{label}的 itemId 应以 {prefix} 开头，收到 {item_id!r}。从 listMyTables 重新拿"

    field_keys = sorted({"fieldName", "fieldNames", "fieldId", "fields", "oldName"} & set(params))
    if field_keys:
        return f"renameNotebookItem 不收 {field_keys}。**列名这套接口改不了**，请用户在页面上改"

    problem = _validate_name(params)
    if problem:
        return problem

    # 服务端会**静默丢弃**没声明的字段
    unknown = sorted(set(params) - ALLOWED_KEYS)
    if unknown:
        if "itemIds" in unknown:
            return "一次只改一个对象，没有批量：itemIds 改成 itemId，逐个调"
        if "icon" in unknown:
            return "这套接口**只能改名字**，图标改不了（请用户在页面上改）。去掉 icon 再调"
        return (
            f"renameNotebookItem 只收 itemType、itemId、name，多了 {unknown}。"
            "服务端会静默丢掉它们 —— 去掉再调（不用传 notebookId，服务端按 itemId 自己找）"
        )
    return None


def _hint(errcode, errmsg):
    """按错误码给一句「接下来怎么办」。errmsg 原文照样打印，这里只补方向。"""
    errmsg = errmsg or ""
    if errcode in UNCERTAIN_ERRCODES:
        return (
            "\n这种结果**说不准改没改**（超时 / 连不上 / 服务端异常），别跟用户说「改好了」，也别说「没改」。"
            "用**同样的** itemType、itemId 和 name 原样重试是安全的：已经改成这个名字的再改一次只会回成功。"
            "也可以先 smart_table.py listMyTables（不是自己建的用 listSharedTables）看名字变没变。"
        )
    head = "\n这次**名字没有改**。"
    if errcode == 400 and "already exists" in errmsg:
        return (
            head + "同一个多维表里已经有一个叫这个名字的文件夹（文件夹不能重名；仪表盘 / 页面 / 应用可以）。"
            "把冲突告诉用户、请他换个名字；**不要自己加后缀或编号重试**。"
        )
    if errcode == 400:
        return (
            head + "多半是名字不合法（去掉首尾空白后要 1–255 字）或 itemType / itemId 不对，按 errmsg 改。"
        )
    if errcode == 403:
        return (
            head + "你对这个多维表没有编辑权（要创建者或「可编辑」）。告诉用户，请多维表的创建者来改，"
            "或请他把你设为「可编辑」。"
        )
    if errcode == 404:
        return (
            head + "itemId 不存在、itemType 与它对不上、它已进回收站（回收站里的改不了名）、它不在任何多维表里、"
            "所在的多维表已进回收站，或者你对那个多维表只有「可查看」（要创建者或「可编辑」才能改）。"
            "用 listMyTables / listSharedTables 重新拿：itemType 取它所在的数组。"
        )
    return head + "按 errmsg 原文改。"


def main():
    argv = sys.argv[1:]
    inline = "--inline" in argv
    # 改名不设确认闸门；顺手带了 --yes 的也认，不当成 JSON 参数
    argv = [a for a in argv if a not in ("--inline", "--yes")]

    if not argv:
        print(
            "Usage: smart_table.py renameNotebookItem "
            '\'{"itemType":"dashboard|folder|page|application","itemId":"...","name":"新名字"}\' [--inline]',
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
