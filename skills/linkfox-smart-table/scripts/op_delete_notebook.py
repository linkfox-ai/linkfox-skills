#!/usr/bin/env python3
"""智能表格-删除多维表（移到回收站）- LinkFox Skill
调用 /smartTable/deleteNotebook 接口。

⚠️ **整包进回收站**：多维表里的数据表、仪表盘、文件夹、页面、应用一起删。
⚠️ **还原只能在页面上**：网页左侧栏底部的「回收站」。这套接口没有还原。
⚠️ **关联列默认拦下**：多维表外有关联列指向里面的表时整条拒绝、什么都不删；
   传 allowBreakingLinks: true 才删，那些列会被转成单行文本，从回收站还原也转不回来。
   这个开关只能在用户看过是哪几列、明确同意之后才加，脚本绝不自己加。
⚠️ **权限**：只有多维表的创建者能删；协作者（「可编辑」「可查看」）一律 404。

必须先拿到用户明确确认再调。默认要求 `--yes`；缺它直接拒绝执行。

Usage:
  python smart_table.py deleteNotebook '{"notebookId":"nbkXXX"}' --yes
  python smart_table.py deleteNotebook '{"notebookId":"nbkXXX","allowBreakingLinks":true}' --yes
"""

import json
import os
import socket
import sys
import time
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API_PATH = "/smartTable/deleteNotebook"
SLUG = "linkfox-smart-table-delete-notebook"

# 响应 <= 该字节数时落盘后额外全量打印到 stdout；超过则只打摘要
SMALL_THRESHOLD = 8000

# 比其余接口的 120 秒长：删多维表要把里面的子资源逐个软删，大多维表要几十秒。
# 超时不代表失败（服务端照样会删完），宁可多等，少一次「确认 → 重试」的往返。
TIMEOUT_SECONDS = 300

ALLOWED_KEYS = {"notebookId", "allowBreakingLinks"}

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
    """打印紧凑摘要。删除的响应很小，只有带走上百张表时才会走到这里。"""
    if not isinstance(result, dict):
        print(f"Response type: {type(result).__name__}")
        print(json.dumps(result, ensure_ascii=False)[:500])
        return
    print(f"Top-level keys: {list(result.keys())}")
    payload = _payload(result)
    for k in ("errcode", "errmsg"):
        if k in result and isinstance(result[k], (int, float, bool, str)):
            print(f"  {k}: {result[k]}")
    for k in ("notebookId", "name", "alreadyInTrash", "hiddenBrokenLinkCount"):
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
    name = payload.get("name")
    notebook_id = payload.get("notebookId")
    if payload.get("alreadyInTrash"):
        print(
            f"多维表「{name}」（{notebook_id}）本来就在回收站里，这次什么都没做。"
            "多半是上一次调用其实已经删成功了（比如超时），或者用户已经在页面上删过。"
            "跟用户说「它已经在回收站里了」，别说「刚删掉了」。"
        )
        return
    print(f"已把多维表「{name}」（{notebook_id}）连同里面的全部内容移到回收站。")
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



# 拿错 id 是最可能的误用：手上有什么 id 就往里塞。按前缀说清它是什么、该走哪条
_WRONG_PREFIX_HINTS = {
    "tbl": (
        "这是数据表 id（tbl 开头），不是多维表 id。只删这一张表 → 用 deleteTable；"
        "真要删它所在的整个多维表 → 先 smart_table.py listMyTables（找不到再 listSharedTables），"
        "在 notebooks[].tables[] 里找到这个 tableId，取它所在那一项的 notebookId 再来"
    ),
    "bnf": "这是文件夹 id（bnf 开头）。删文件夹用 deleteNotebookItem，itemType 传 \"folder\"",
    "pag": "这是页面 id（pag 开头）。删页面用 deleteNotebookItem，itemType 传 \"page\"",
    "apl": "这是应用 id（apl 开头）。删应用用 deleteNotebookItem，itemType 传 \"application\"",
    "dsh": "这是仪表盘 id（dsh 开头）。删仪表盘用 deleteNotebookItem，itemType 传 \"dashboard\"",
    "shr": "这是分享 id（shr 开头），不能拿来删东西。用 listMyTables 找到多维表的 notebookId",
}


def _validate(params):
    if not isinstance(params, dict):
        return "参数必须是 JSON 对象"

    notebook_id = params.get("notebookId")
    if not notebook_id:
        if params.get("tableId"):
            return (
                "deleteNotebook 删的是**整个多维表**，要 notebookId（nbk 开头），不收 tableId。"
                "只删一张数据表 → 用 deleteTable；真要删整个多维表 → 用 listMyTables 查出它的 notebookId"
            )
        if params.get("itemId") or params.get("itemType"):
            return "删多维表里的仪表盘 / 文件夹 / 页面 / 应用 → 用 deleteNotebookItem，不是 deleteNotebook"
        return (
            "缺少 notebookId（nbk 开头）。用 smart_table.py listMyTables（找不到再 listSharedTables）"
            "按名字找到 notebooks[].notebookId"
        )
    if not isinstance(notebook_id, str):
        return f"notebookId 必须是字符串，收到 {notebook_id!r}"
    if not notebook_id.startswith("nbk"):
        hint = _WRONG_PREFIX_HINTS.get(notebook_id[:3])
        return (
            f"notebookId 必须以 nbk 开头，收到 {notebook_id!r}。"
            + (hint or "用 smart_table.py listMyTables 查 notebooks[].notebookId")
        )

    if "allowBreakingLinks" in params and not isinstance(params["allowBreakingLinks"], bool):
        return "allowBreakingLinks 必须是 true / false（默认 false）"

    # 服务端会**静默丢弃**没声明的字段：带着 tableId 调过来，删掉的是整个多维表而不是那张表
    unknown = sorted(set(params) - ALLOWED_KEYS)
    if unknown:
        return (
            f"deleteNotebook 只收 notebookId、allowBreakingLinks，多了 {unknown}。"
            "服务端会静默丢掉它们、照样删整个多维表 —— 只想删其中一部分就换 deleteTable / deleteNotebookItem；"
            "确实要删整个多维表就去掉这些参数再调"
        )
    return None



def _refuse_without_yes(params):
    extra = ""
    if params.get("allowBreakingLinks"):
        extra = (
            "\n⚠️ 你还传了 allowBreakingLinks: true —— 多维表外指向里面的表的关联列会被转成单行文本，"
            "从回收站还原也转不回来。只有用户看过是哪几列（先不带它调一次，报错里会列出来）、"
            "明确同意之后才能带它。"
        )
    print(
        f"拒绝执行：这会把多维表 {params['notebookId']} **连同里面的全部内容**"
        "（数据表、仪表盘、文件夹、页面、应用）一起移到回收站。"
        f"还原只能由用户在网页左侧栏底部的「回收站」里操作，这套接口没有还原。{extra}\n"
        "先用 smart_table.py listMyTables（不是自己建的就用 listSharedTables）找到这个 notebookId，"
        "向用户复述：多维表叫什么、里面有哪些数据表（tables）、仪表盘（dashboards）、"
        "文件夹（folders）、页面（pages）、应用（applications）会一起被删；"
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
            "先用 smart_table.py listMyTables 看这个多维表还在不在：不在了就是已经删掉了；"
            "还在就原样重试 —— 已经进了回收站的再删会回 alreadyInTrash，不会出事。"
        )
    head = "\n这次**什么都没有删**。"
    if errcode == 400 and "关联列" in errmsg:
        return (
            head + "多维表外还有关联列指向里面的表（errmsg 里列了是哪几列）。"
            "删下去这些列会被转成单行文本，从回收站还原也转不回来。"
            "把这些列原样告诉用户、拿到明确同意，再传 allowBreakingLinks: true 并加 --yes 重跑。"
            "**不要自己直接加上重试。**"
        )
    if errcode == 404:
        return (
            head + "多维表不存在、不在你当前团队里，或者你不是它的创建者"
            "（只有这两种人能删整个多维表，其余协作者一律回 404）。"
            "用 listMyTables / listSharedTables 核对 notebookId；是别人的多维表就请创建者来删。"
        )
    if errcode == 409:
        return (
            head + "这个多维表里有另一个删除还在进行。等一会儿，先用 listMyTables 确认那一次的结果，"
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
            "Usage: smart_table.py deleteNotebook "
            '\'{"notebookId":"nbkXXX"}\' --yes [--inline]',
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
