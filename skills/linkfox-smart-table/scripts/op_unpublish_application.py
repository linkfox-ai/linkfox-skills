#!/usr/bin/env python3
"""智能表格-取消发布应用 - LinkFox Skill
调用 /smartTable/unpublishApplication 接口。

把**已经发布上线**的应用下线：发布地址清空、可见性回 `private`、公开分享凭据一并撤销。
走的跟 ui2 那个「取消发布」按钮是**同一条**服务逻辑，入参也一样，只是换成网关这条路进来。
身份来自网关注入的头，脚本不传任何用户/团队参数。

⚠️ **不可逆的部分**：如果这个应用曾经**公开分享**过，取消发布会把那条公开凭据（`publicShareId`）
一起撤销，**撤了回不来** —— 之后重新发布为「公开」会铸一条**新的**链接，原来发出去的旧链接永久失效。
下线前如果用户是把链接发给了别人，要先说清这一点。

⚠️ **幂等**：重复取消发布是安全的，上游照常成功，本地也是同一个结果。不像发布那样会撞 409。

⚠️ **失败时本地一个字节都不写**：上游失败整条回失败，`publishUrl` 保持原样
（可能还是上次发布的地址）。**别把失败当成「已下线」**。

入参：
  applicationId  必填。应用在我们这边的关联行 id（`apl` 开头）。**不是 `sessionId`**。
                 取 `listApplications` 出参的 `applicationId`，或 `createApplication` 出参的同名字段；
                 两个列表接口里的 `applications[].itemId` 也是同一个值。
                 跨团队 / 不存在的 id 一律回 404（故意不区分，防探测）。

出参（一层扁平，与 publishApplication 同形）：
  applicationId  回显下线的是哪个应用
  notebookId     应用所在的多维表
  sessionId      这个应用绑定的会话 id（可能为 null，存量应用的正常回退）
  publishUrl     **恒为 null** —— 取消发布成功后发布地址已被清空。留这个字段只为与发布接口同形，
                 别拿它当「发布地址丢了」的异常

权限：能往这个应用所在多维表里写东西的人才能下线（与创建 / 发布同一道容器写权门）。
容器角色是创建者 / 可编辑可以；「可查看」和无权一律回 404，不是 403。

Usage:
  python smart_table.py unpublishApplication '{"applicationId":"aplXxx0000001"}'
"""

import json
import os
import sys
import time
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API_PATH = "/smartTable/unpublishApplication"
SLUG = "linkfox-smart-table-unpublish-application"

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
        # 服务端到上游的超时是 60s，这边留一倍余量，别在服务端还没回包时就先断开
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
    """打印紧凑摘要。下线没有地址要拿，摘要就是把回显字段摆出来。"""
    if not isinstance(result, dict):
        print(f"Response type: {type(result).__name__}")
        print(json.dumps(result, ensure_ascii=False)[:500])
        return
    print(f"Top-level keys: {list(result.keys())}")
    for k in ("errcode", "errmsg", "applicationId", "notebookId", "sessionId", "publishUrl"):
        value = result.get(k)
        if isinstance(value, (int, float, bool, str)) or value is None:
            print(f"  {k}: {value}")


def _resolve_output_path(ts):
    """落到 <cwd>/linkfox/<date>/<session>/data/<slug>-<ts>.json。"""
    return resolve_data_path(SLUG, ts)


def _validate(params):
    if not isinstance(params, dict):
        return "参数必须是 JSON 对象"

    application_id = params.get("applicationId")
    if application_id is None:
        return (
            "applicationId 必填：应用在我们这边的关联行 id（apl 开头），不是 sessionId。"
            "用 listApplications 按应用名查，出参里就有 applicationId"
        )
    if not isinstance(application_id, str) or not application_id.strip():
        return "applicationId 必须是非空字符串（apl 开头的应用 id）"

    session_id = params.get("sessionId")
    if session_id is not None:
        return (
            "sessionId 不需要传：取消发布按 applicationId 定位，用哪个会话由服务端从应用关联行上取。"
            "把 applicationId 传进来就行"
        )
    return None


def main():
    argv = sys.argv[1:]
    inline = "--inline" in argv
    argv = [a for a in argv if a != "--inline"]

    if not argv:
        print(
            "applicationId 必填。用法：python smart_table.py unpublishApplication "
            '\'{"applicationId":"<listApplications 里的 applicationId>"}\'',
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
        if result.get("errcode") == 404:
            # 三种成因故意不区分：应用不存在 / 不在你的团队 / 那个多维表你只有「可查看」
            print(
                "提示：404 有三种成因且故意不区分 —— 这个 applicationId 不存在、"
                "它不在你的团队里、或者那个应用所在的多维表你只有「可查看」。"
                "上线状态**没变**（还是发布中的样子）。用 listApplications 重新确认真实的 applicationId。",
                file=sys.stderr,
            )
        elif result.get("errcode") == 400:
            print(
                "提示：400 多半是调用失败或这个应用没有可下线的会话（存量应用的 sessionId 为空）。"
                "上线状态**没变**。",
                file=sys.stderr,
            )
        else:
            print(
                "提示：失败时本地一个字节都没写，`publishUrl` 保持原样（多半还是上次发布的地址）。"
                "**别当成「已下线」** —— 用 listApplications 确认那个应用当前是不是还没下线。",
                file=sys.stderr,
            )
    elif isinstance(result, dict):
        if result.get("publishUrl") is not None:
            # 取消发布这一步清的就是 publishUrl，还有值说明这次没真正下线
            print(
                "注意：出参 `publishUrl` 不是 null，这次**不算下线成功**。"
                "用 listApplications 看那个应用的 `publishUrl` / `publishVisibility`，别直接当成已下线。"
            )

    if inline or len(serialized.encode("utf-8")) <= SMALL_THRESHOLD:
        print(serialized)
    else:
        summarize(result)


if __name__ == "__main__":
    main()
