#!/usr/bin/env python3
"""智能表格-删除数据表（移到回收站）- LinkFox Skill
调用 /smartTable/deleteTable 接口。

⚠️ **整张表进回收站**：记录、字段、视图一起走。还原只能由用户在网页左侧栏底部的「回收站」里操作，
   这套接口没有还原。
⚠️ **多维表至少要留一张数据表**：删的是最后一张会 400。要删光就用 deleteNotebook 删整个多维表；
   只是想换一张，先 addTable 新建再删这张。
⚠️ **关联列默认拦下**：别的表有关联列指向这张表时整条拒绝、什么都不删；传 allowBreakingLinks: true
   才删，那些列会被转成单行文本，从回收站还原也转不回来。这个开关脚本绝不自己加。
⚠️ **自动化**：以这张表为触发表的工作流会被置空触发表（流本身保留，但不会再被触发）。
⚠️ **权限**：只有这张表的创建者，或它所在多维表的创建者能删；其余人 403。

必须先拿到用户明确确认再调。默认要求 `--yes`；缺它直接拒绝执行。

Usage:
  python smart_table.py deleteTable '{"tableId":"tblXXX"}' --yes
  python smart_table.py deleteTable '{"tableId":"tblXXX","allowBreakingLinks":true}' --yes
"""

import json
import os
import socket
import sys
import time
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API_PATH = "/smartTable/deleteTable"
SLUG = "linkfox-smart-table-delete-table"

# 响应 <= 该字节数时落盘后额外全量打印到 stdout；超过则只打摘要
SMALL_THRESHOLD = 8000

TIMEOUT_SECONDS = 120

ALLOWED_KEYS = {"tableId", "allowBreakingLinks"}

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
    """打印紧凑摘要。删除的响应很小，正常走不到这里。"""
    if not isinstance(result, dict):
        print(f"Response type: {type(result).__name__}")
        print(json.dumps(result, ensure_ascii=False)[:500])
        return
    print(f"Top-level keys: {list(result.keys())}")
    payload = _payload(result)
    for k in ("errcode", "errmsg"):
        if k in result and isinstance(result[k], (int, float, bool, str)):
            print(f"  {k}: {result[k]}")
    for k in ("tableId", "name", "notebookId", "alreadyInTrash", "hiddenBrokenLinkCount"):
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
    table_id = payload.get("tableId")
    if payload.get("alreadyInTrash"):
        print(
            f"数据表「{name}」（{table_id}）本来就在回收站里，这次什么都没做。"
            "多半是上一次调用其实已经删成功了（比如超时），或者用户已经在页面上删过。"
            "跟用户说「它已经在回收站里了」，别说「刚删掉了」。"
        )
        return
    where = f"（所在多维表 {payload.get('notebookId')}）" if payload.get("notebookId") else ""
    print(f"已把数据表「{name}」（{table_id}）{where}移到回收站。")
    _print_broken_links(payload)
    print(
        "如果有自动化（工作流）以这张表为触发表，它们已被置空触发表：流还在，但不会再被触发，"
        "要恢复得让用户到工作流侧重新选表并保存。"
    )
    print(
        "要还原请用户到网页左侧栏底部的「回收站」里操作；这套接口没有还原。"
        "回收站里放满 30 天会被自动彻底删除，找不回来。"
    )


def _resolve_output_path(ts):
    """落到 <cwd>/linkfox/<date>/<session>/data/<slug>-<ts>.json。"""
    return resolve_data_path(SLUG, ts)



# 拿错 id 是最可能的误用：手上有什么 id 就往里塞。按前缀说清它是什么、该走哪条
_WRONG_PREFIX_HINTS = {
    "nbk": (
        "这是多维表 id（nbk 开头），不是数据表 id。要删整个多维表（连同里面全部内容）→ 用 deleteNotebook；"
        "只删其中一张表 → 用 listMyTables 在 notebooks[].tables[] 里找到那张表的 tableId"
    ),
    "bnf": "这是文件夹 id（bnf 开头）。删文件夹用 deleteNotebookItem，itemType 传 \"folder\"",
    "pag": "这是页面 id（pag 开头）。删页面用 deleteNotebookItem，itemType 传 \"page\"",
    "apl": "这是应用 id（apl 开头）。删应用用 deleteNotebookItem，itemType 传 \"application\"",
    "dsh": "这是仪表盘 id（dsh 开头）。删仪表盘用 deleteNotebookItem，itemType 传 \"dashboard\"",
    "fld": "这是字段 id（fld 开头）。删列用 deleteFields（按列名删），不是 deleteTable",
    "rec": "这是记录 id（rec 开头）。删行用 deleteRecords，不是 deleteTable",
    "viw": "这是视图 id（viw 开头）。视图删不了，用 listMyTables 找数据表的 tableId",
}


def _validate(params):
    if not isinstance(params, dict):
        return "参数必须是 JSON 对象"

    table_id = params.get("tableId")
    if not table_id:
        if params.get("notebookId"):
            return (
                "deleteTable 删的是一张数据表，要 tableId（tbl 开头），不收 notebookId。"
                "要删整个多维表 → 用 deleteNotebook；只删其中一张 → 用 listMyTables 找到它的 tableId"
            )
        if params.get("itemId") or params.get("itemType"):
            return "删多维表里的仪表盘 / 文件夹 / 页面 / 应用 → 用 deleteNotebookItem，不是 deleteTable"
        return (
            "缺少 tableId（tbl 开头）。用 smart_table.py listMyTables（找不到再 listSharedTables）"
            "按表名找到它"
        )
    if not isinstance(table_id, str):
        return f"tableId 必须是字符串，收到 {table_id!r}"
    if not table_id.startswith("tbl"):
        hint = _WRONG_PREFIX_HINTS.get(table_id[:3])
        return (
            f"tableId 必须以 tbl 开头，收到 {table_id!r}。"
            + (hint or "用 smart_table.py listMyTables 按表名找到它")
        )

    if "allowBreakingLinks" in params and not isinstance(params["allowBreakingLinks"], bool):
        return "allowBreakingLinks 必须是 true / false（默认 false）"

    # 服务端会**静默丢弃**没声明的字段。最危险的是照着 deleteRecords / deleteFields 的习惯带了
    # recordIds / fieldNames：以为只删几行几列，实际整张表进了回收站
    unknown = sorted(set(params) - ALLOWED_KEYS)
    if unknown:
        if {"recordIds", "fieldNames"} & set(unknown):
            return (
                f"deleteTable 删的是**整张表**，不收 {unknown}。"
                "只删几行 → deleteRecords；只删几列 → deleteFields。真要删整张表就去掉这些参数再调"
            )
        return (
            f"deleteTable 只收 tableId、allowBreakingLinks，多了 {unknown}。"
            "服务端会静默丢掉它们 —— 去掉再调（一次只删一张表，没有批量）"
        )
    return None



def _refuse_without_yes(params):
    extra = ""
    if params.get("allowBreakingLinks"):
        extra = (
            "\n⚠️ 你还传了 allowBreakingLinks: true —— 别的表里指向这张表的关联列会被转成单行文本，"
            "从回收站还原也转不回来。只有用户看过是哪几列（先不带它调一次，报错里会列出来）、"
            "明确同意之后才能带它。"
        )
    print(
        f"拒绝执行：这会把数据表 {params['tableId']}（连同它的全部记录、字段、视图）移到回收站；"
        "以它为触发表的自动化会被置空触发表、不再触发。"
        f"还原只能由用户在网页左侧栏底部的「回收站」里操作，这套接口没有还原。{extra}\n"
        "先用 smart_table.py listMyTables（不是自己建的就用 listSharedTables）找到这个 tableId，"
        "向用户复述：表叫什么、在哪个多维表里；想说清连带影响可以再用 listWorkflows 看有没有流以它为触发表；"
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
            "先用 smart_table.py listMyTables 看这张表还在不在：不在了就是已经删掉了；"
            "还在就原样重试 —— 已经进了回收站的再删会回 alreadyInTrash，不会出事。"
        )
    head = "\n这次**什么都没有删**。"
    if errcode == 400 and "关联列" in errmsg:
        return (
            head + "别的表里还有关联列指向这张表（errmsg 里列了是哪几列）。"
            "删下去这些列会被转成单行文本，从回收站还原也转不回来。"
            "把这些列原样告诉用户、拿到明确同意，再传 allowBreakingLinks: true 并加 --yes 重跑。"
            "**不要自己直接加上重试。**"
        )
    if errcode == 400 and "至少要保留" in errmsg:
        return (
            head + "这是多维表里最后一张数据表，多维表至少要留一张。"
            "用户要把整个多维表删掉 → 用 deleteNotebook；只是想换一张 → 先 addTable 新建，再删这张。"
        )
    if errcode == 403:
        return (
            head + "只有这张表的创建者、或它所在多维表的创建者能删（能看、能改都不够）。"
            "告诉用户请表的创建者来删。"
        )
    if errcode == 404:
        return head + "表不存在，或不在你当前团队里。用 listMyTables / listSharedTables 重新拿 tableId。"
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
            "Usage: smart_table.py deleteTable "
            '\'{"tableId":"tblXXX"}\' --yes [--inline]',
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
