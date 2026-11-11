#!/usr/bin/env python3
"""智能表格-创建应用 - LinkFox Skill
调用 /smartTable/createApplication 接口。

**按模板**在一个**已有多维表**里建一个应用。返回它的 applicationId、**进编辑器的 sessionId**，
以及 `sourceUrl` —— 那个应用源代码包（tar.gz）的下载地址，下载后自己改代码用。
身份来自网关注入的头，脚本不传任何用户/团队参数。

⚠️ **这个操作不幂等**：每次调用都会让应用服务新建一个会话、我们这边新建一行应用。
超时 / 断连 / 拿不准成没成时，**先 `listApplications` 看有没有多出这个应用**，
确认没建出来再重试 —— 直接重发会多出一个应用（还多一个用不上的会话）。

⚠️ **同一时间只能建一个**：上一个创建请求还没跑完就又调一次，会回
`errcode=409`「已有应用正在创建中」。这是按**用户**挡的（不是按多维表、也不是按模板），
等上一个跑完再调；这把锁最长 2 分钟自己过期。

入参：
  notebookId  必填。建在哪个多维表下，nbk 开头。取 listMyTables / listSharedTables
              顶层 notebooks[].notebookId，或 createTable / copyNotebook 的出参。
              传数据表 id（tbl 开头）会 404，本地先拦一次。
  templateId  必填。用哪个**应用模板**建。从 listOfficialTemplates 拿
              （`{"templateType":"app"}`），取每条模板的 **`resourceId`**（短横线 slug，
              如 `blank-template`）。每条模板还有 32 位十六进制的 `id`，那个只给
              listOfficialTemplates 自己按 id 精确筛选用 —— 传它会回 424
              `App template directory not found`。
              它不是 notebookId、也不是本地路径。
  name        可选，1~255 字。不传用「应用」。

出参（一层扁平）：
  notebookId     回显建在了哪个容器里
  applicationId  我们这边关联行的 id（apl 开头）；删 / 改名时当 itemId 用
  sessionId      进应用编辑器的会话 id。理论上必回，null 只在存量数据里出现
  sourceUrl      应用源代码包地址（tar.gz），下载后自己改代码。**我们不存它**：
                 上游没给就是 null（应用照样建好了），要再拿得重新建一个应用
  name           应用名（回采自服务端，不是回显入参）

同一个多维表里用同一个模板建多个应用是**正常需求**，不拦（`notebookId`+`templateId`
重复完全合法）。

权限：能往这个多维表里建数据表的人才能建应用（同一个容器写权门）。
多维表不存在 / 进了回收站 / 不在我团队 → 404，三种不区分。

Usage:
  python smart_table.py createApplication '{"notebookId":"nbkXXX","templateId":"<模板 resourceId>"}'
  python smart_table.py createApplication '{"notebookId":"nbkXXX","templateId":"<模板 resourceId>","name":"库存看板"}'
"""

import json
import os
import sys
import time
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API_PATH = "/smartTable/createApplication"
SLUG = "linkfox-smart-table-create-application"

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
    """打印紧凑摘要。应用只有一个，摘要就是把那三四个字段摆出来。"""
    if not isinstance(result, dict):
        print(f"Response type: {type(result).__name__}")
        print(json.dumps(result, ensure_ascii=False)[:500])
        return
    print(f"Top-level keys: {list(result.keys())}")
    # 出参里没有 templateId（服务端不回显），别在这里列它，免得打出一个假的 None
    for k in ("errcode", "errmsg", "notebookId", "applicationId", "name", "sessionId", "sourceUrl"):
        value = result.get(k)
        if isinstance(value, (int, float, bool, str)) or value is None:
            print(f"  {k}: {value}")


def _resolve_output_path(ts):
    """落到 <cwd>/linkfox/<date>/<session>/data/<slug>-<ts>.json。"""
    return resolve_data_path(SLUG, ts)


def _validate(params):
    if not isinstance(params, dict):
        return "参数必须是 JSON 对象"
    notebook_id = params.get("notebookId")
    if notebook_id is None:
        return 'notebookId 必填：要建在哪个多维表下（nbk 开头），从 listMyTables / listSharedTables 出参拿'
    if not isinstance(notebook_id, str) or not notebook_id:
        return "notebookId 必须是非空字符串"
    # 传数据表 id 会得到 404「Notebook tblxxx not found」，很容易被误读成「这个多维表不存在」。
    if notebook_id.startswith("tbl"):
        return (
            "notebookId 传的是数据表 id（tbl 开头）。这里要的是**多维表**id："
            "取 listMyTables / listSharedTables 顶层 notebooks[].notebookId，不是里面的 tables[].tableId。"
        )
    template_id = params.get("templateId")
    if template_id is None:
        return (
            "templateId 必填：用哪个应用模板建。先调 listOfficialTemplates"
            '（{"templateType":"app"}）取每条模板的 resourceId（不是 32 位 id）'
            " —— 不是 notebookId，也不是本地路径"
        )
    if not isinstance(template_id, str) or not template_id.strip():
        return (
            "templateId 必须是非空字符串"
            "（从 listOfficialTemplates 的 templateType=app 结果里取 resourceId，"
            "不是 id —— 传 id 会回 424）"
        )
    name = params.get("name")
    if name is not None and (not isinstance(name, str) or not name.strip()):
        return "name 必须是非空字符串，或整个省略（省略时用「应用」）"
    return None


def main():
    argv = sys.argv[1:]
    inline = "--inline" in argv
    argv = [a for a in argv if a != "--inline"]

    if not argv:
        print(
            "notebookId 和 templateId 都必填。用法：python smart_table.py createApplication "
            '\'{"notebookId":"nbkXXX","templateId":"<模板 resourceId>"}\'',
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

    # 业务失败不靠 HTTP 状态码判断，看 errcode（这个接口 HTTP 恒 200，错误码在 body 里）
    if isinstance(result, dict) and result.get("errcode") != 200:
        errmsg = str(result.get("errmsg") or "")
        print(
            f"Business error: errcode={result.get('errcode')} errmsg={errmsg}",
            file=sys.stderr,
        )
        if result.get("errcode") == 409 and "已有应用正在创建中" in errmsg:
            # 按用户挡的锁，不是这个多维表/模板被占了
            print(
                "提示：409 是「你上一个创建应用的请求还没跑完」（同一时间只能建一个，"
                "跟多维表、模板无关）。稍等再调即可；这把锁最长 2 分钟自己过期。"
                "这种情况下**没有**建出应用，不是失败重试。",
                file=sys.stderr,
            )
        elif result.get("errcode") == 409:
            # 另一种 409：sessionId 撞唯一约束（极少见），跟那把创建锁无关，可以直接重新发起
            print(
                "提示：这个 409 不是「已有应用正在创建中」，而是本次会话 id 已被占用（极少见）。"
                "**没有**建出应用，重新发起一次创建即可。",
                file=sys.stderr,
            )
        else:
            # 上游会话创建不幂等：失败也可能已经建出来了，提醒先确认，别直接重发
            print(
                "提示：这个操作**不幂等**。如果这次是超时 / 连接失败（不是 404 / 403 这类明确拒绝），"
                "先用 listApplications 看有没有多出这个应用，确认没建出来再重试。",
                file=sys.stderr,
            )
    elif isinstance(result, dict):
        if not result.get("sessionId"):
            print(
                "注意：出参没有 sessionId，这个应用**进不去编辑器**（正常创建理论上必回）。"
                "应用本身已经建好了，用 applicationId 走页面；要再拿会话得重新建一个应用。"
            )
        # sourceUrl 我们**不落库**，这次没拿到就再也拿不到（除非重建一个应用）
        if not result.get("sourceUrl"):
            print(
                "注意：出参没有 sourceUrl（上游没给），改不了这个应用的源代码。"
                "应用本身已经建好了，走页面改；要拿源码得重新建一个应用。"
            )

    if inline or len(serialized.encode("utf-8")) <= SMALL_THRESHOLD:
        print(serialized)
    else:
        summarize(result)


if __name__ == "__main__":
    main()
