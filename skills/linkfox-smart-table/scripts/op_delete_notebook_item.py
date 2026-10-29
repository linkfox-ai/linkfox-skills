#!/usr/bin/env python3
"""智能表格-删除多维表里的仪表盘 / 文件夹 / 页面 / 应用（移到回收站）- LinkFox Skill
调用 /smartTable/deleteNotebookItem 接口。

itemType 四选一：dashboard / folder / page / application；itemId 从 listMyTables / listSharedTables
里那个多维表的 dashboards / folders / pages / applications 数组拿，itemType 就是它所在的那个数组。
「页面」指多维表侧栏里的页面节点，与 linkfox-smart-table-page 技能（生成页面）不是一回事。

⚠️ **删文件夹 = 连里面的东西一起删**：数据表、仪表盘、页面、应用、子文件夹全部进回收站。
   还要求里面每张数据表你都能单独删（表或多维表的创建者），否则 403、什么都不删；
   文件夹装着多维表的全部数据表时 400（多维表至少要留一张）。
⚠️ **还原只能在页面上**：网页左侧栏底部的「回收站」。这套接口没有还原。
⚠️ **关联列默认拦下**（只有删文件夹会碰到）：别处有关联列指向文件夹里的表时整条拒绝、什么都不删；
   传 allowBreakingLinks: true 才删，那些列会被转成单行文本，从回收站还原也转不回来。脚本绝不自己加。
⚠️ **权限**：所在多维表的创建者，或「可编辑」的协作者。不在任何多维表里的一律 404。

必须先拿到用户明确确认再调。默认要求 `--yes`；缺它直接拒绝执行。

Usage:
  python smart_table.py deleteNotebookItem '{"itemType":"dashboard","itemId":"dshXXX"}' --yes
  python smart_table.py deleteNotebookItem '{"itemType":"folder","itemId":"bnfXXX"}' --yes
  python smart_table.py deleteNotebookItem '{"itemType":"folder","itemId":"bnfXXX","allowBreakingLinks":true}' --yes
"""

import json
import os
import socket
import sys
import time
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API_PATH = "/smartTable/deleteNotebookItem"
SLUG = "linkfox-smart-table-delete-notebook-item"

# 响应 <= 该字节数时落盘后额外全量打印到 stdout；超过则只打摘要
SMALL_THRESHOLD = 8000

# 比其余接口的 120 秒长：删文件夹要把里面的子资源逐个软删，大文件夹要几十秒。
# 超时不代表失败（服务端照样会删完），宁可多等，少一次「确认 → 重试」的往返。
TIMEOUT_SECONDS = 300

ALLOWED_KEYS = {"itemType", "itemId", "allowBreakingLinks"}

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

# 这几种结果说不准删没删：超时 / 连不上 / 网关超时 / 服务端异常。
# 别按「什么都没删」解读，也别按「删好了」解读 —— 先用列表接口确认。
UNCERTAIN_ERRCODES = {0, 500, 502, 503, 504}

# 列表最多打印几行，再多只给数量（完整内容在落盘文件里）
MAX_LISTED = 50

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
        "errmsg": (
            f"等待超时（{TIMEOUT_SECONDS} 秒）。删除可能还在服务端进行，**不代表失败，也不代表删好了**"
        ),
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
    """打印紧凑摘要。删除的响应很小，只有文件夹带走上百张表时才会走到这里。"""
    if not isinstance(result, dict):
        print(f"Response type: {type(result).__name__}")
        print(json.dumps(result, ensure_ascii=False)[:500])
        return
    print(f"Top-level keys: {list(result.keys())}")
    payload = _payload(result)
    for k in ("errcode", "errmsg"):
        if k in result and isinstance(result[k], (int, float, bool, str)):
            print(f"  {k}: {result[k]}")
    for k in ("itemType", "itemId", "name", "notebookId", "alreadyInTrash", "hiddenBrokenLinkCount"):
        if k in payload and isinstance(payload[k], (int, float, bool, str)):
            print(f"  {k}: {payload[k]}")



def _print_broken_links(payload):
    """关联列被转成了单行文本 —— 从回收站还原也转不回来，必须告诉用户。"""
    broken = payload.get("brokenLinks") or []
    hidden = payload.get("hiddenBrokenLinkCount") or 0
    if not broken and not hidden:
        return
    print("⚠️ 这些关联列已被转成单行文本（从回收站还原也转不回来），要告诉用户：")
    for link in broken[:MAX_LISTED]:
        if isinstance(link, dict):
            print(f"  「{link.get('tableName')}」的「{link.get('fieldName')}」  ({link.get('tableId')})")
    if len(broken) > MAX_LISTED:
        print(f"  …… 另有 {len(broken) - MAX_LISTED} 列，见落盘文件")
    if hidden:
        print(f"  另有 {hidden} 列在你没有权限查看的表里")


def _report(payload):
    """给 agent 的结论：删了什么、怎么跟用户说。"""
    label = ITEM_TYPES.get(payload.get("itemType"), (payload.get("itemType"),))[0]
    name = payload.get("name")
    item_id = payload.get("itemId")
    if payload.get("alreadyInTrash"):
        print(
            f"{label}「{name}」（{item_id}）本来就在回收站里，这次什么都没做。"
            "多半是上一次调用其实已经删成功了（比如超时），或者用户已经在页面上删过。"
            "跟用户说「它已经在回收站里了」，别说「刚删掉了」。"
        )
        return
    print(f"已把{label}「{name}」（{item_id}，所在多维表 {payload.get('notebookId')}）移到回收站。")
    if payload.get("itemType") == "folder":
        print("文件夹里的仪表盘、页面、应用、子文件夹也一起进了回收站。")
    tables = payload.get("trashedTables") or []
    if tables:
        print(f"一起进回收站的数据表 {len(tables)} 张：")
        for table in tables[:MAX_LISTED]:
            if isinstance(table, dict):
                print(f"  - {table.get('name')!r}  {table.get('tableId')}")
        if len(tables) > MAX_LISTED:
            print(f"  …… 另有 {len(tables) - MAX_LISTED} 张，见落盘文件")
    _print_broken_links(payload)
    print(
        "要还原请用户到网页左侧栏底部的「回收站」里操作；这套接口没有还原。"
        "回收站里放满 30 天会被自动彻底删除，找不回来。"
    )


def _resolve_output_path(ts):
    """落到 <cwd>/linkfox/<date>/<session>/data/<slug>-<ts>.json。"""
    return resolve_data_path(SLUG, ts)



# id 前缀 → 它其实是哪种 itemType（用来在 itemType 与 itemId 对不上时给出准确的改法）
_TYPE_BY_PREFIX = {"bnf": "folder", "pag": "page", "apl": "application", "dsh": "dashboard"}


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
        return "删数据表用 deleteTable（传 tableId），不是 deleteNotebookItem"
    if lowered in ("notebook", "notebooks", "base"):
        return "删整个多维表用 deleteNotebook（传 notebookId），不是 deleteNotebookItem"
    if lowered in ("workflow", "workflows", "automation"):
        return "工作流（自动化）不在这里删：让用户到工作流侧删，删完会自动同步到多维表"
    fixed = ITEM_TYPE_ALIASES.get(lowered) or (lowered if lowered in ITEM_TYPES else None)
    if fixed:
        return f"itemType 写成了 {item_type!r}，应为 {fixed!r}（单数、全小写）"
    return f"itemType 只能是 dashboard / folder / page / application，收到 {item_type!r}"


def _validate(params):
    if not isinstance(params, dict):
        return "参数必须是 JSON 对象"

    item_id = params.get("itemId")
    if not item_id:
        if params.get("tableId"):
            return "删数据表用 deleteTable（传 tableId），不是 deleteNotebookItem"
        if params.get("notebookId"):
            return (
                "deleteNotebookItem 要 itemType + itemId，不收 notebookId。"
                "要删整个多维表 → 用 deleteNotebook；删其中的仪表盘 / 文件夹 / 页面 / 应用 → "
                "从 listMyTables 里那个多维表的 dashboards / folders / pages / applications 拿 itemId"
            )
        return (
            "缺少 itemId。从 smart_table.py listMyTables（找不到再 listSharedTables）里那个多维表的 "
            "dashboards / folders / pages / applications 数组拿"
        )
    if not isinstance(item_id, str):
        return f"itemId 必须是字符串，收到 {item_id!r}"
    if len(item_id) > 64:
        return f"itemId 太长（{len(item_id)} 字），不像是列表里拿到的 id"

    # 先认 tbl / nbk：这两种走的根本不是这条接口，说清楚比报「itemType 不对」有用
    if item_id.startswith("tbl"):
        return f"itemId={item_id!r} 是数据表 id（tbl 开头）。删数据表用 deleteTable（传 tableId）"
    if item_id.startswith("nbk"):
        return (
            f"itemId={item_id!r} 是多维表 id（nbk 开头）。删整个多维表（连同里面全部内容）用 deleteNotebook"
        )

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

    if "allowBreakingLinks" in params and not isinstance(params["allowBreakingLinks"], bool):
        return "allowBreakingLinks 必须是 true / false（默认 false）"

    unknown = sorted(set(params) - ALLOWED_KEYS)
    if unknown:
        if "itemIds" in unknown:
            return "一次只删一个对象，没有批量：itemIds 改成 itemId，逐个调"
        return (
            f"deleteNotebookItem 只收 itemType、itemId、allowBreakingLinks，多了 {unknown}。"
            "服务端会静默丢掉它们 —— 去掉再调（不用传 notebookId，服务端按 itemId 自己找）"
        )
    return None



def _refuse_without_yes(params):
    item_type = params["itemType"]
    label, array_name, _ = ITEM_TYPES[item_type]
    extra = ""
    if params.get("allowBreakingLinks"):
        extra = (
            "\n⚠️ 你还传了 allowBreakingLinks: true —— 别处指向文件夹里那些表的关联列会被转成单行文本，"
            "从回收站还原也转不回来。只有用户看过是哪几列（先不带它调一次，报错里会列出来）、"
            "明确同意之后才能带它。"
        )
    if item_type == "folder":
        scope = (
            f"这会把文件夹 {params['itemId']} **连同里面的全部内容**（数据表、仪表盘、页面、应用、子文件夹）"
            "一起移到回收站。"
        )
        enumerate_hint = (
            "向用户复述：文件夹叫什么、在哪个多维表里，以及里面有什么 —— 各数组里 folderId 等于它的"
            "数据表（tables）、仪表盘、页面、应用、子文件夹都会被带走，子文件夹里的再按它的 id 往下找；"
        )
    else:
        scope = f"这会把{label} {params['itemId']} 移到回收站。"
        enumerate_hint = f"向用户复述：{label}叫什么、在哪个多维表里；"
    print(
        f"拒绝执行：{scope}"
        f"还原只能由用户在网页左侧栏底部的「回收站」里操作，这套接口没有还原。{extra}\n"
        f"先用 smart_table.py listMyTables（不是自己建的就用 listSharedTables），在那个多维表的 "
        f"{array_name} 里找到这个 itemId，{enumerate_hint}"
        "拿到明确确认，再加 --yes 重跑。",
        file=sys.stderr,
    )
    sys.exit(2)


def _hint(errcode, errmsg):
    """按错误码给一句「接下来怎么办」。errmsg 原文照样打印，这里只补方向。"""
    errmsg = errmsg or ""
    if errcode in UNCERTAIN_ERRCODES:
        return (
            "\n这种结果**说不准删没删**（超时 / 连不上 / 服务端异常），别跟用户说「删好了」，也别说「没删」。"
            "先用 smart_table.py listMyTables 看它还在不在对应的数组里：不在了就是已经删掉了；"
            "还在就原样重试 —— 已经进了回收站的再删会回 alreadyInTrash，不会出事。"
        )
    head = "\n这次**什么都没有删**。"
    if errcode == 400 and "关联列" in errmsg:
        return (
            head + "文件夹外还有关联列指向文件夹里的表（errmsg 里列了是哪几列）。"
            "删下去这些列会被转成单行文本，从回收站还原也转不回来。"
            "把这些列原样告诉用户、拿到明确同意，再传 allowBreakingLinks: true 并加 --yes 重跑。"
            "**不要自己直接加上重试。**"
        )
    if errcode == 400 and "至少要保留" in errmsg:
        return (
            head + "这个文件夹装着多维表的全部数据表，删了多维表就一张表都不剩了（至少要留一张）。"
            "用户要把整个多维表删掉 → 用 deleteNotebook；否则先 addTable 新建一张（或让用户在页面上"
            "把要留的表挪出文件夹），再删文件夹。"
        )
    if errcode == 403:
        return (
            head + "你对这个多维表没有编辑权（要创建者或「可编辑」）；删的是文件夹的话，"
            "也可能是里面有你不能单独删的数据表（只有表或多维表的创建者能删表）。"
            "告诉用户，请多维表的创建者来删。"
        )
    if errcode == 404:
        return (
            head + "itemId 不存在、itemType 与它对不上、它不在任何多维表里，或者它所在的多维表已经进了回收站。"
            "用 listMyTables / listSharedTables 重新拿：itemType 取它所在的数组。"
        )
    if errcode == 409:
        return (
            head + "同一个多维表里有另一个删除还在进行。等一会儿，先用 listMyTables 确认那一次的结果，"
            "需要的话再重试。"
        )
    return head + "按 errmsg 原文改。"



def main():
    argv = sys.argv[1:]
    inline = "--inline" in argv
    confirmed = "--yes" in argv
    argv = [a for a in argv if a not in ("--inline", "--yes")]

    if not argv:
        print(
            "Usage: smart_table.py deleteNotebookItem "
            '\'{"itemType":"dashboard|folder|page|application","itemId":"..."}\' --yes [--inline]',
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
        _refuse_without_yes(params)

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
    _report(_payload(result))


if __name__ == "__main__":
    main()
