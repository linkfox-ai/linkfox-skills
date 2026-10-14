#!/usr/bin/env python3
"""智能表格-附件列上传图片 - LinkFox Skill
调用 /smartTable/uploadAttachment 接口。

往附件列（type: attachment）的**一格**里**追加一张**图片：服务端按图片地址下载、存进表格自己的存储、
追加到这一格已有附件的末尾。只追加不覆盖，一次一张。

图片来源二选一：
  - imageUrl：公网可访问的 http/https 图片地址，直接交给服务端下载；
  - imagePath：本地图片文件路径。脚本先把它传到平台 OSS 拿到公开地址，再交给服务端。

Usage:
  python smart_table.py uploadAttachment '{"tableId":"tblXXX","recordId":"recXXX","fieldName":"商品图","imageUrl":"https://..."}'
  python smart_table.py uploadAttachment '{"tableId":"tblXXX","recordId":"recXXX","fieldName":"商品图","imagePath":"./a.png"}'
  python smart_table.py uploadAttachment '<JSON>' --inline
"""

import json
import os
import sys
import time
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API_PATH = "/smartTable/uploadAttachment"
SLUG = "linkfox-smart-table-upload-attachment"

# 响应 <= 该字节数时落盘后额外全量打印到 stdout；超过则只打摘要
SMALL_THRESHOLD = 8000

# 与服务端单张上限一致（20MB）。本地图片先在这里拦，省一次 OSS 上传
MAX_IMAGE_BYTES = 20 * 1024 * 1024

# 本地图片只收这些扩展名。服务端按下载到的 Content-Type 判 image/*，这里是提前给一句人话
IMAGE_EXTS = {"png", "jpg", "jpeg", "gif", "webp", "bmp", "svg"}

# linkfox_paths.py 由 scaffold 从 linkfoxagent-v2/_shared 复制到本目录 scripts/，原样不改。
from linkfox_paths import get_api_base, resolve_data_path, upload_file


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
        # 服务端要先下载图片再入桶，比普通写接口慢
        with urlopen(req, timeout=180) as response:
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
    """打印紧凑摘要：顶层字段 + 追加的那一项附件。"""
    if not isinstance(result, dict):
        print(f"Response type: {type(result).__name__}")
        print(json.dumps(result, ensure_ascii=False)[:500])
        return

    print(f"Top-level keys: {list(result.keys())}")
    for k in ("errcode", "errmsg", "recordId", "fieldName"):
        if k in result and isinstance(result[k], (int, float, bool, str)):
            print(f"  {k}: {result[k]}")
    attachment = result.get("attachment")
    if isinstance(attachment, dict):
        print("\nAttachment:")
        print(json.dumps(attachment, indent=2, ensure_ascii=False))


def _resolve_output_path(ts):
    """落到 <cwd>/linkfox/<date>/<session>/data/<slug>-<ts>.json。"""
    return resolve_data_path(SLUG, ts)


def _validate(params):
    """本地预检：把明显的入参错误在发请求前挡掉，省一次往返。"""
    if not isinstance(params, dict):
        return "参数必须是 JSON 对象"
    if not params.get("tableId"):
        return "缺少 tableId（以 tbl 开头）"
    if not params.get("recordId"):
        return (
            "缺少 recordId（以 rec 开头）。图片要追加到某一行的某一格里；"
            "还没有这一行就先用 smart_table.py createRecords 新增，拿返回的 recordId"
        )
    if not params.get("fieldName"):
        return "缺少 fieldName（附件列的字段名）"
    has_url = bool(params.get("imageUrl"))
    has_path = bool(params.get("imagePath"))
    if has_url == has_path:
        return "imageUrl 和 imagePath 必须且只能给一个（公网图片地址，或本地图片文件路径）"
    if has_url and not str(params["imageUrl"]).lower().startswith(("http://", "https://")):
        return "imageUrl 只支持 http/https 地址。本地文件请改用 imagePath"
    if has_path:
        path = params["imagePath"]
        if not os.path.isfile(path):
            return f"imagePath 指向的文件不存在：{path}"
        ext = os.path.splitext(path)[1].lstrip(".").lower()
        if ext not in IMAGE_EXTS:
            return f"imagePath 不是图片文件（扩展名 .{ext}）。只支持：{', '.join(sorted(IMAGE_EXTS))}"
        if os.path.getsize(path) > MAX_IMAGE_BYTES:
            return f"图片超过 20MB 上限：{path}"
    return None


def _to_request_body(params, ts):
    """imagePath → 先传平台 OSS 换成公开地址；服务端只收 imageUrl。"""
    body = {k: params[k] for k in ("tableId", "recordId", "fieldName")}
    if params.get("imageUrl"):
        body["imageUrl"] = params["imageUrl"]
        return body
    try:
        uploaded = upload_file(params["imagePath"], slug=SLUG, ts=ts)
    except RuntimeError as e:
        print(f"本地图片上传失败：{e}", file=sys.stderr)
        sys.exit(1)
    print(f"Local image uploaded: {uploaded['url']}")
    body["imageUrl"] = uploaded["url"]
    return body


def main():
    argv = sys.argv[1:]
    inline = "--inline" in argv
    argv = [a for a in argv if a != "--inline"]

    if not argv:
        print(
            f"Usage: smart_table.py uploadAttachment "
            '\'{"tableId":"tblXXX","recordId":"recXXX","fieldName":"附件列名","imageUrl":"https://..."}\' [--inline]',
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

    ts = int(time.time())
    result = call_api(_to_request_body(params, ts))

    serialized = json.dumps(result, ensure_ascii=False, indent=2)
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

    if inline or len(serialized.encode("utf-8")) <= SMALL_THRESHOLD:
        print(serialized)
    else:
        summarize(result)


if __name__ == "__main__":
    main()
