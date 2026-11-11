#!/usr/bin/env python3
"""智能表格-发布应用 - LinkFox Skill
调用 /smartTable/publishApplication 接口。

把**改完代码**的应用重新发布上线，回发布地址 `publishUrl`。身份来自网关注入的头，脚本不传任何用户/团队参数。

典型链条（外部 agent 改代码的场景）：
  1. `createApplication` → 出参拿 `sessionId` 和 `sourceUrl`（源码包 tar.gz 的**下载**地址）
  2. agent 下载源码、改代码
  3. agent 把改完的**整个代码包**传到自己的 OSS / S3 / 任意可访问的存储，拿到一个**新的**地址
  4. `publishApplication` 传 `{sessionId, sourceUrl: <第 3 步的新地址>}` → 出参 `publishUrl` 就是发布地址

⚠️ **`sourceUrl` 不是创建接口给的那个地址**。创建接口给的是**下载**地址（原始代码），
这里要的是**你自己上传的、改完之后**的代码包地址。传错了发布会把原始代码发上线（或者直接失败）。

⚠️ **发布不幂等**：上游是「把这个 session 的当前代码上线」，同一个 session 重复发是安全的
（幂等），但**并发**发同一个 session 会被挡回 `errcode=409`「这个应用正在发布中…」——
按 `sessionId` 挡的，跟多维表无关，锁最长 2 分钟自己过期。

⚠️ **失败时本地一个字节都不写**：上游失败（424）整条回失败，`publishUrl` 保持原样（可能是旧的、
也可能是空）。别把失败当成「已下线」。

入参：
  sessionId  必填。创建接口返回的、进应用编辑器的会话 id，**绑在那一行应用上**。
             不是 applicationId、不是 notebookId。用它定位应用（跨团队 / 不存在的会话都回 404）。
  sourceUrl  必填。**改完之后自己上传**的代码包地址（tar.gz）。我们只透传给上游，
             不下载、不解析、不落库。不校验 URL 形状（OSS / S3 / 预签名各有各的样子）。

出参（一层扁平）：
  applicationId  我们这边关联行的 id（apl 开头）
  notebookId     应用所在的多维表
  sessionId      回显发布的是哪个会话
  publishUrl     发布地址（上游字段叫 appUrl）。**已落库**到应用的发布字段，ui2 侧栏 / 详情页
                 直接显示「已发布」，两个列表接口（listApplications）也读它

权限：能往这个应用所在多维表里写东西的人才能发布（同一个容器写权门）。
容器角色是创建者 / 可编辑可以；「可查看」和无权一律回 404，不是 403。

Usage:
  python smart_table.py publishApplication '{"sessionId":"<创建接口返回的 sessionId>","sourceUrl":"<改完代码包的上传地址>"}'
"""

import json
import os
import sys
import time
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API_PATH = "/smartTable/publishApplication"
SLUG = "linkfox-smart-table-publish-application"

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
    """打印紧凑摘要。发布只有一个地址要拿，摘要就是把那几个字段摆出来。"""
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

    session_id = params.get("sessionId")
    if session_id is None:
        return (
            "sessionId 必填：**创建应用接口返回的**那个 sessionId（进应用编辑器的会话 id），"
            "不是 applicationId、也不是 notebookId。丢了就用 listApplications 按应用名查回来"
        )
    if not isinstance(session_id, str) or not session_id.strip():
        return "sessionId 必须是非空字符串"

    source_url = params.get("sourceUrl")
    if source_url is None:
        return (
            "sourceUrl 必填：**改完代码之后自己上传**的代码包地址（tar.gz）。"
            "它不是创建接口返回的那个下载地址 —— 那个是原始代码，这里是改完的"
        )
    if not isinstance(source_url, str) or not source_url.strip():
        return "sourceUrl 必须是非空字符串（改完代码包的公网可读地址）"
    return None


def main():
    argv = sys.argv[1:]
    inline = "--inline" in argv
    argv = [a for a in argv if a != "--inline"]

    if not argv:
        print(
            "sessionId 和 sourceUrl 都必填。用法：python smart_table.py publishApplication "
            '\'{"sessionId":"<创建接口返回的>","sourceUrl":"<改完代码包地址>"}\'',
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
            # 三种成因故意不区分：会话不存在 / 不在你的团队 / 那个多维表你只有「可查看」
            print(
                "提示：404 有三种成因且故意不区分 —— 这个 sessionId 不存在（或不是创建接口给的）、"
                "它不在你的团队里、或者那个应用所在的多维表你只有「可查看」。"
                "上线状态**没变**（还是上次发布的样子）。用 listApplications 重新确认真实的 sessionId。",
                file=sys.stderr,
            )
        elif result.get("errcode") == 409:
            print(
                "提示：409 是「同一个应用上一次发布还没跑完」（按 sessionId 挡的，跟多维表无关），"
                "锁最长 2 分钟自己过期。这次**没有**发布，等它跑完再用**同样的参数**发一次。",
                file=sys.stderr,
            )
        else:
            print(
                "提示：失败时本地一个字节都没写，`publishUrl` 保持原样（可能是上一次发布的地址，"
                "也可能是空）。别当成「已下线」—— 要下线得走取消发布那条路。",
                file=sys.stderr,
            )
    elif isinstance(result, dict):
        if not result.get("publishUrl"):
            # 这个字段就是这条接口的目的，取不到按失败处理（服务端那边也会当失败）
            print(
                "注意：出参没有 publishUrl，这次发布**不算成功**（服务端把「取不到发布地址」当失败）。"
                "用 listApplications 看那个应用当前是不是已发布，别直接当成发布好了。"
            )

    if inline or len(serialized.encode("utf-8")) <= SMALL_THRESHOLD:
        print(serialized)
    else:
        summarize(result)


if __name__ == "__main__":
    main()
