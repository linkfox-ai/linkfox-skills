#!/usr/bin/env python3
"""智能表格-复制多维表（创建副本 / 分享另存为副本）- LinkFox Skill
调用 /smartTable/copyNotebook 接口。

两个入口，二选一，效果与页面上一致：
  · notebookId —— 页面的「创建副本」：只能复制**你创建的、或你是多维表协作者的**多维表
    （listMyTables / listSharedTables 里能看到的那些）。
  · shareUrl（+ password）—— 分享页的「另存为副本」：只有分享人设成「可另存为副本」的链接能复制，
    「可查看」「可编辑」的链接一律拒绝。设了密码的链接要带 password。

副本连同里面的数据表、仪表盘、自动化（工作流）、页面一起复制，**一律**落在你自己团队里、归你本人。
默认连记录一起复制（includeRecords 默认 true，与页面一致）。

复制可能要几十秒到几分钟。脚本会自动带一个 requestKey（没传时生成一个并打印出来）：
超时后**先用 listMyTables 确认副本是不是已经建好**，没有再用**同一个 requestKey** 重试，
别换 key 重新提交——那样会复制出两份。

Usage:
  python smart_table.py copyNotebook '{"notebookId":"nbkXXXX"}'
  python smart_table.py copyNotebook '{"notebookId":"nbkXXXX","name":"选品台账（Q4）","includeRecords":false}'
  python smart_table.py copyNotebook '{"shareUrl":"https://os.linkfox.com/share/shrXXXX/base"}'
  python smart_table.py copyNotebook '{"shareUrl":"https://os.linkfox.com/share/shrXXXX/base","password":"1234"}'
"""

import json
import os
import re
import socket
import sys
import time
import uuid
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API_PATH = "/smartTable/copyNotebook"
SLUG = "linkfox-smart-table-copy-notebook"

# 响应 <= 该字节数时落盘后额外全量打印到 stdout；超过则只打摘要
SMALL_THRESHOLD = 8000

# 比其余接口的 120 秒长：复制是一次大事务，带记录的大多维表要几十秒到几分钟。
# 超时本身不是失败（服务端照样会复制完），所以宁可多等，少一次「确认 → 重试」的往返。
TIMEOUT_SECONDS = 300

# 「副本建好了，但某一类外挂资源没完整跟过来」的旗标 → 给用户看的名字。服务端只在为真时带上
COPY_FAILED_FLAGS = (
    ("workflowCopyFailed", "自动化（工作流）"),
    ("pageCopyFailed", "页面"),
    ("applicationCopyFailed", "应用"),
)

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


def _timeout_result(request_key):
    return {
        "errcode": 0,
        "errmsg": (
            f"等待超时（{TIMEOUT_SECONDS} 秒）。复制可能还在服务端进行，**不代表失败**。"
            "先用 smart_table.py listMyTables 看副本是不是已经出现；"
            f"没有的话用同一个 requestKey（{request_key}）重试，别换 key —— 换 key 会复制出两份"
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
        # 读超时在不同 Python 版本里不一定包成 URLError，单独接住：这条接口超时是常态而不是故障
        return _timeout_result(params.get("requestKey"))
    except URLError as e:
        if isinstance(e.reason, (socket.timeout, TimeoutError)):
            return _timeout_result(params.get("requestKey"))
        return {"errcode": 0, "errmsg": f"Connection failed: {e.reason}"}


def summarize(result):
    """打印紧凑摘要：副本是谁、里面有哪些表（tableId 后续读写要用）。"""
    if not isinstance(result, dict):
        print(f"Response type: {type(result).__name__}")
        print(json.dumps(result, ensure_ascii=False)[:500])
        return
    print(f"Top-level keys: {list(result.keys())}")
    for k in (
        "errcode",
        "errmsg",
        "notebookId",
        "name",
        "url",
        "idempotentHit",
        "workflowCopyFailed",
        "pageCopyFailed",
        "applicationCopyFailed",
    ):
        if k in result and isinstance(result[k], (int, float, bool, str)):
            print(f"  {k}: {result[k]}")
    tables = result.get("tables")
    if isinstance(tables, list):
        print(f"  tables ({len(tables)}):")
        for table in tables:
            if isinstance(table, dict):
                print(f"    - {table.get('tableId')}  {table.get('name')}")


def _resolve_output_path(ts):
    """落到 <cwd>/linkfox/<date>/<session>/data/<slug>-<ts>.json。"""
    return resolve_data_path(SLUG, ts)


# 与后端 parseShareId 同一个口径：裸 shrXXX，或地址里 /share/shrXXX 那一段
_BARE_SHARE_ID = re.compile(r"^shr[0-9a-zA-Z]+$")
_SHARE_IN_URL = re.compile(r"/share/(shr[0-9a-zA-Z]+)(?:[/?#]|$)")
# 站内页面地址：多维表页 /table/<bse>/notebook/<nbk>、数据表页 /table/<bse>/<tbl>
_NOTEBOOK_PAGE = re.compile(r"/notebook/(nbk[0-9a-zA-Z]+)")
_TABLE_PAGE = re.compile(r"/table/bse[0-9a-zA-Z]+/(tbl[0-9a-zA-Z]+)")


def _check_share_url(value):
    """shareUrl 必须是分享链接。最常见的误用是把站内页面地址当分享链接传（10-16 测试线实踩过）。"""
    text = value.strip()
    if _BARE_SHARE_ID.match(text) or _SHARE_IN_URL.search(text):
        return None
    notebook_page = _NOTEBOOK_PAGE.search(text)
    if notebook_page:
        return (
            "shareUrl 给的是多维表页面地址，不是分享链接。这个多维表你本来就能看到，走「创建副本」："
            f"改传 notebookId={notebook_page.group(1)}"
        )
    table_page = _TABLE_PAGE.search(text)
    if table_page:
        table_id = table_page.group(1)
        return (
            f"shareUrl 给的是数据表页面地址，不是分享链接。这张表（tableId={table_id}）你本来就能看到，"
            "走「创建副本」：先 smart_table.py listMyTables（找不到再 listSharedTables），在 "
            f"notebooks[].tables[] 里找到 tableId={table_id} 的那一项，取它所在多维表的 notebookId，"
            "再调 copyNotebook 传 notebookId"
        )
    return "shareUrl 不是分享链接：应形如 https://<host>/share/shrXXXX/base（或直接给 shr 开头的分享 id）"


def _validate(params):
    """本地预检。把 agent 最容易填错的几处在发请求前挡掉，并给出人话原因。"""
    if not isinstance(params, dict):
        return "参数必须是 JSON 对象"

    notebook_id = params.get("notebookId")
    share_url = params.get("shareUrl")

    if not notebook_id and not share_url:
        if params.get("tableId"):
            return (
                "copyNotebook 复制的是整个多维表，要的是 notebookId（`nbk` 开头），不是 tableId。"
                "用 smart_table.py listMyTables / listSharedTables 查：表所在的那个多维表的 id 在 "
                "notebooks[].notebookId 里"
            )
        return (
            "notebookId 和 shareUrl 要传一个：复制你自己能看到的多维表传 notebookId"
            "（从 listMyTables / listSharedTables 拿），按别人发的分享链接另存传 shareUrl"
        )
    if notebook_id and share_url:
        return "notebookId 和 shareUrl 只能传一个：前者是「创建副本」，后者是「分享另存为副本」"

    if notebook_id and not str(notebook_id).startswith("nbk"):
        return (
            f"notebookId={notebook_id!r} 看起来不是多维表 id —— 它应该以 `nbk` 开头。"
            "`tbl` 开头的是数据表 id；`shr` 开头的是分享 id，应该放进 shareUrl"
        )
    if share_url:
        problem = _check_share_url(str(share_url))
        if problem:
            return problem
    if "password" in params and not share_url:
        return "password 只能和 shareUrl 一起传（它是分享链接的访问密码）"
    if "includeRecords" in params and not isinstance(params["includeRecords"], bool):
        return "includeRecords 必须是 true / false（默认 true，连记录一起复制）"
    name = params.get("name")
    if name is not None and (not isinstance(name, str) or not name.strip()):
        return "name 要么不传（自动命名），要么是非空字符串"
    return None


def _hint(errcode, params):
    """按错误码给一句「接下来怎么办」。errmsg 原文照样打印，这里只补方向。"""
    if errcode == 404:
        if params.get("shareUrl"):
            return "\n这条分享链接已经失效（被关闭了，或者分享的多维表进了回收站）。请分享人重新发一条。"
        return (
            "\n这个多维表你看不到：不是你创建的、你也不是它的协作者，或者它不在你当前团队里 / 已进回收站。"
            "用 listMyTables / listSharedTables 重新查 notebookId；"
            "只被加进了其中某张表（不是整个多维表）的协作者也复制不了整个多维表。"
        )
    if errcode == 403:
        return "\n分享人没有给这条链接开「可另存为副本」。请对方把链接权限改成「可另存为副本」后再试。"
    if errcode == 409:
        return (
            "\n有复制还在进行中。别换 requestKey 重新提交：等一会儿先用 listMyTables 确认副本是否已建好，"
            "需要再复制一个就等这个完成后再发。"
        )
    return ""


def main():
    argv = sys.argv[1:]
    inline = "--inline" in argv
    argv = [a for a in argv if a != "--inline"]

    if not argv:
        print(
            "Usage: smart_table.py copyNotebook "
            '\'{"notebookId":"nbkXXXX"}\' 或 \'{"shareUrl":"https://.../share/shrXXXX/base","password":"..."}\''
            " [--inline]",
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

    # 没传幂等键就补一个，并打印出来：超时重试时必须用同一个，脚本自己记不住跨进程的状态
    if not params.get("requestKey"):
        params["requestKey"] = f"copy-{uuid.uuid4()}"
    print(f"requestKey: {params['requestKey']}（超时重试时用同一个）")

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
            f"Business error: errcode={result.get('errcode')} errmsg={result.get('errmsg')}"
            f"{_hint(result.get('errcode'), params)}",
            file=sys.stderr,
        )
    elif isinstance(result, dict) and any(result.get(key) for key, _ in COPY_FAILED_FLAGS):
        # 副本是建好了的；只是其中一部分没跟过来。要让用户知道，别说「全部复制成功」
        missing = "、".join(label for key, label in COPY_FAILED_FLAGS if result.get(key))
        print(f"注意：副本已建好，但其中的{missing}没有完整复制过来，请让用户到副本里核对", file=sys.stderr)

    if inline or len(serialized.encode("utf-8")) <= SMALL_THRESHOLD:
        print(serialized)
    else:
        summarize(result)


if __name__ == "__main__":
    main()
