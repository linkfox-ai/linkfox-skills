#!/usr/bin/env python3
"""智能表格-我的应用列表 - LinkFox Skill
调用 /smartTable/listApplications 接口。

列出**当前团队内、我能看到的全部应用**（多维表里 type=application 的节点）：
我创建的多维表下的应用 + 别人共享给我的多维表下的应用。身份来自网关注入的头，脚本不传任何用户/团队参数。

⚠️ 出参是**一层**的扁平列表（与 listMyTables / listSharedTables 的两层形状不同）：
applications[] 每项自带 notebookId（它属于哪个多维表）和 notebookName，total 是**应用数**不是容器数。

⚠️ sessionId 是**进应用编辑器的对话 id**，也正是这个接口存在的理由。它可能是 null
（存量应用、或创建时出站失败）—— null 表示进不去编辑器，不是错误，别当异常处理。

每个应用还带 source（mine=我创建 / shared=协作给我）、publishUrl / publishVisibility
（public=已公开分享，private 或没分享过就没有 URL）、folderId（在哪个文件夹里，可能不返回）。

入参全可选、可叠加：
  name          应用名，**包含匹配**（大小写不敏感），不用给全名
  notebookId    只看这一个多维表；它看不见或不存在时 404（两者不区分，防探测）
  notebookName  多维表名，包含匹配；命中多个多维表就列出这些多维表下的全部应用
  source        mine | shared | all（默认 all）
  page/perPage  默认第 1 页、每页 100

Usage:
  python smart_table.py listApplications                                  # 全部应用
  python smart_table.py listApplications '{"name":"销量"}'                 # 按应用名找
  python smart_table.py listApplications '{"notebookName":"门店"}'          # 按多维表名找
  python smart_table.py listApplications '{"source":"shared"}'             # 只看协作给我的
  python smart_table.py listApplications '{"notebookId":"nbkXXX","page":2}' # 指定多维表 + 分页
  python smart_table.py listApplications '{}' --inline                    # 强制全量打印到 stdout
"""

import json
import os
import sys
import time
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API_PATH = "/smartTable/listApplications"
SLUG = "linkfox-smart-table-list-applications"

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
    """打印紧凑摘要。一行一个应用：名字 + applicationId + sessionId + 所属多维表。"""
    if not isinstance(result, dict):
        print(f"Response type: {type(result).__name__}")
        print(json.dumps(result, ensure_ascii=False)[:500])
        return
    print(f"Top-level keys: {list(result.keys())}")
    for k in ("errcode", "errmsg", "total", "perPage", "currentPage"):
        if k in result and isinstance(result[k], (int, float, bool, str)):
            print(f"  {k}: {result[k]}")

    rows = result.get("applications")
    if not isinstance(rows, list):
        return
    print()
    print(f"应用 {len(rows)} 个（当前页；total 是应用总数）：")
    for row in rows:
        if not isinstance(row, dict):
            continue
        session = row.get("sessionId") or "<无，进不去编辑器>"
        tag = "我创建" if row.get("source") == "mine" else "协作"
        public = "  [已公开]" if row.get("publishVisibility") == "public" else ""
        print(
            f"  - {row.get('name')!r}  applicationId={row.get('applicationId')}  "
            f"sessionId={session}  ({tag}){public}"
        )
        notebook = row.get("notebookName")
        folder = f"  文件夹={row.get('folderId')}" if row.get("folderId") else ""
        print(f"      多维表={notebook!r}  notebookId={row.get('notebookId')}{folder}")
    if result.get("total") and len(rows) < result.get("total"):
        print(f"  还有更多：用 page 翻页（total={result.get('total')}，本页 {len(rows)} 条）。")


def _resolve_output_path(ts):
    """落到 <cwd>/linkfox/<date>/<session>/data/<slug>-<ts>.json。"""
    return resolve_data_path(SLUG, ts)


def _validate(params):
    if not isinstance(params, dict):
        return "参数必须是 JSON 对象"
    for key in ("name", "notebookId", "notebookName"):
        value = params.get(key)
        if value is None:
            continue
        if not isinstance(value, str) or not value:
            return f"{key} 必须是非空字符串，或整个省略"
    source = params.get("source")
    if source is not None and source not in ("mine", "shared", "all"):
        return f"source 只能是 mine / shared / all（收到 {source!r}），或整个省略（= all）"
    notebook_id = params.get("notebookId")
    # 传数据表 id 会得到 404「Notebook tblxxx not found」，很容易被误读成「这个多维表不存在」。
    if isinstance(notebook_id, str) and notebook_id.startswith("tbl"):
        return (
            "notebookId 传的是数据表 id（tbl 开头）。这里要的是**多维表**id："
            "取 listMyTables / listSharedTables 顶层 notebooks[].notebookId，不是里面的 tables[].tableId。"
        )
    return None


def main():
    argv = sys.argv[1:]
    inline = "--inline" in argv
    argv = [a for a in argv if a != "--inline"]

    # 无参即全部：这个接口所有入参都是可选的
    if not argv:
        params = {}
    else:
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
        rows = result.get("applications") or []
        if not rows:
            # 空列表是成功，但成因有好几种，别让调用方只报「没有应用」
            print(
                "空结果。可能：确实没有应用；名称 / 多维表名没匹配上（两者都是包含匹配）；"
                "或者那些多维表当前身份看不见（只被共享了其中某几张数据表的，看不到里面的应用）。"
            )
        else:
            no_session = [r.get("name") for r in rows if isinstance(r, dict) and not r.get("sessionId")]
            if no_session:
                print(
                    f"注意：{len(no_session)} 个应用**没有 sessionId**，进不去编辑器（不是错误，通常是存量应用）："
                    f"{no_session[:10]}。要打开只能用 applicationId 走页面。"
                )

    if inline or len(serialized.encode("utf-8")) <= SMALL_THRESHOLD:
        print(serialized)
    else:
        summarize(result)


if __name__ == "__main__":
    main()
