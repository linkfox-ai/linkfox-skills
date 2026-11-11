#!/usr/bin/env python3
"""智能表格-附件列上传文件 - LinkFox Skill
调用 /smartTable/uploadAttachment 接口（一条路由，按入参分三种模式）。

往附件列（type: attachment）的**一格**里**追加一个**文件：只追加不覆盖，一次一个。

三种用法，按入参自动选：

  - imageUrl：公网可访问的 http/https 地址，服务端自己下载后入桶。适合网上现成的文件。
  - filePath（旧名 imagePath）：本地文件。脚本走三步：申请上传地址 → 文件**直传 S3**（不经过本服务，
    不占服务端带宽和临时盘）→ 带 uploadId 完成。适合手上有文件。
  - uploadId：文件已经传完、只差「完成」这一步时，用它收尾。完成是幂等的，重复调用不会让一格挂两份。
    （PUT 中途断了、或者别的工具已经把文件直传上去，都用这个。）

类型：任意文件（与页面上传一致）。大小按类型分档：图片 20MB、视频 50MB、Excel（xls/xlsx）50MB，
其余不设专门上限、由全局阈值兜底（也是 50MB）。服务端按**文件实测**的类型与大小再判一次，传超了会在完成时被拒。

出了事怎么续：脚本在申请到上传地址后就把它连同 uploadId 落盘（见输出里的 Saved upload ticket），
直传失败时用 ticketPath 指回那个文件重跑，脚本会复用同一个 uploadId 而不是重新申请。

Usage:
  python smart_table.py uploadAttachment '{"tableId":"tblXXX","recordId":"recXXX","fieldName":"商品图","imageUrl":"https://..."}'
  python smart_table.py uploadAttachment '{"tableId":"tblXXX","recordId":"recXXX","fieldName":"资料","filePath":"./手册.pdf"}'
  python smart_table.py uploadAttachment '{"tableId":"tblXXX","recordId":"recXXX","fieldName":"商品视频","ticketPath":"/.../ticket-xxx.json"}'
  python smart_table.py uploadAttachment '{"tableId":"tblXXX","recordId":"recXXX","fieldName":"商品图","uploadId":"xxxxxxx"}'
  python smart_table.py uploadAttachment '<JSON>' --inline
"""

import json
import mimetypes
import os
import sys
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

API_PATH = "/smartTable/uploadAttachment"
SLUG = "linkfox-smart-table-upload-attachment"

# 响应 <= 该字节数时落盘后额外全量打印到 stdout；超过则只打摘要
SMALL_THRESHOLD = 8000

# 与服务端 getAttachmentMaxSize 同一套口径：图片 20MB、视频 50MB、Excel 50MB；
# 其余类型没有专门档位，落到全局阈值 MAX_ATTACHMENT_UPLOAD_SIZE（默认 50MB）。本地先拦一次，省一次白传
IMAGE_MAX_BYTES = 20 * 1024 * 1024
VIDEO_MAX_BYTES = 50 * 1024 * 1024
EXCEL_MAX_BYTES = 50 * 1024 * 1024
OTHER_MAX_BYTES = 50 * 1024 * 1024

# 「Excel」只算 xls/xlsx。刻意不含 text/csv —— 服务端也只认这两个 mimetype
EXCEL_MIMES = {
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}

# mimetypes 依赖各机器上的系统映射表（Windows 还会读注册表），常用类型在这里钉死
# Content-Type 是签进上传 URL 的，事后改不了；office 文件猜成 octet-stream 的话页面只会显示成通用文件
EXT_TO_MIME = {
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "gif": "image/gif",
    "webp": "image/webp",
    "bmp": "image/bmp",
    "svg": "image/svg+xml",
    "mp4": "video/mp4",
    "m4v": "video/x-m4v",
    "mov": "video/quicktime",
    "webm": "video/webm",
    "avi": "video/x-msvideo",
    "mkv": "video/x-matroska",
    "mpg": "video/mpeg",
    "mpeg": "video/mpeg",
    "ogv": "video/ogg",
    "pdf": "application/pdf",
    "doc": "application/msword",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "xls": "application/vnd.ms-excel",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "ppt": "application/vnd.ms-powerpoint",
    "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "csv": "text/csv",
    "txt": "text/plain",
    "zip": "application/zip",
    "mp3": "audio/mpeg",
    "m4a": "audio/mp4",
    "wav": "audio/wav",
}

# 直传的兜底超时（秒）。urlopen 的 timeout 是单次 socket 操作，不是总时长
PUT_TIMEOUT = 300

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
        # imageUrl 模式服务端要先下载整个文件再入桶，比普通写接口慢得多
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


def put_file(url, upload_method, request_headers, path, size):
    """把本地文件原样 PUT 到预签名地址。返回 None 表示成功，否则返回一句错误原因。

    Content-Type 是**签进 URL 的**，必须按 requestHeaders 原样带上；写完再改不了。
    文件用句柄直接交给 urllib，不整体读进内存（50MB 视频在 agent 容器里很容易把内存吃满）。
    """
    headers = dict(request_headers or {})
    # S3 的预签名 PUT 不接受 chunked，长度必须自己给
    headers.setdefault("Content-Length", str(size))
    last_error = ""
    for attempt in (1, 2):
        try:
            with open(path, "rb") as fh:
                req = Request(url, data=fh, headers=headers, method=upload_method or "PUT")
                with urlopen(req, timeout=PUT_TIMEOUT) as response:
                    if 200 <= response.status < 300:
                        return None
                    last_error = f"HTTP {response.status}"
        except HTTPError as e:
            body = e.read().decode("utf-8", "replace") if e.fp else ""
            last_error = f"HTTP {e.code}: {e.reason} {body[:300]}".strip()
            # 4xx 是签名/请求本身的问题，重试没有意义
            if 400 <= e.code < 500:
                return last_error
        except (URLError, OSError) as e:
            last_error = str(getattr(e, "reason", e))
        if attempt == 1:
            print(f"Direct upload failed ({last_error}), retrying once...", file=sys.stderr)
            time.sleep(2)
    return last_error


def guess_content_type(path, override=None):
    if override:
        return override
    ext = os.path.splitext(path)[1].lstrip(".").lower()
    if ext in EXT_TO_MIME:
        return EXT_TO_MIME[ext]
    guessed, _ = mimetypes.guess_type(path)
    return guessed or "application/octet-stream"


def _max_bytes(content_type):
    """按类型定档。其余类型没有专门档位，给全局阈值那一档（与服务端 MAX_ATTACHMENT_UPLOAD_SIZE 对齐）。"""
    if content_type.startswith("video/"):
        return VIDEO_MAX_BYTES
    if content_type.startswith("image/"):
        return IMAGE_MAX_BYTES
    if content_type in EXCEL_MIMES:
        return EXCEL_MAX_BYTES
    return OTHER_MAX_BYTES


def _size_label(content_type):
    """报错里说人话，与服务端 getAttachmentSizeLabel 一致。"""
    if content_type.startswith("video/"):
        return "视频"
    if content_type.startswith("image/"):
        return "图片"
    if content_type in EXCEL_MIMES:
        return "Excel"
    return "文件"


def _human_size(size):
    return f"{size / (1024 * 1024):.1f}MB"


def _check_type_size(content_type, size, label):
    """本地预检：类型不设限，只按类型分档判大小（服务端完成后还会按实测再判一次）。"""
    if not content_type:
        return f"{label}的类型没认出来，请显式传 contentType（如 application/pdf）"
    try:
        size = int(size)
    except (TypeError, ValueError):
        return f"{label}大小不可用：{size!r}"
    if size <= 0:
        return f"{label}是空文件（0 字节）"
    limit = _max_bytes(content_type)
    if size > limit:
        return f"{_size_label(content_type)}最大 {_human_size(limit)}，{label}是 {_human_size(size)}"
    return None


def _validate(params):
    """本地预检：把明显的入参错误在发请求前挡掉，省一次往返。"""
    if not isinstance(params, dict):
        return "参数必须是 JSON 对象"
    if not params.get("tableId"):
        return "缺少 tableId（以 tbl 开头）"
    if not params.get("recordId"):
        return (
            "缺少 recordId（以 rec 开头）。文件要追加到某一行的某一格里；"
            "还没有这一行就先用 smart_table.py createRecords 新增，拿返回的 recordId"
        )
    if not params.get("fieldName"):
        return "缺少 fieldName（附件列的字段名）"

    local_path = params.get("filePath") or params.get("imagePath")
    wanted = {
        "imageUrl": bool(params.get("imageUrl")),
        "本地文件（filePath/imagePath）": bool(local_path),
        "uploadId": bool(params.get("uploadId")),
        "ticketPath": bool(params.get("ticketPath")),
    }
    given = [name for name, on in wanted.items() if on]
    if len(given) > 1:
        return f"{'、'.join(given)} 必须且只能给一个"
    if not given:
        return (
            "缺少上传方式：给 imageUrl（公网地址）、filePath（本地文件）、"
            "uploadId（已传完只差完成）或 ticketPath（续传）之一"
        )

    if params.get("imageUrl") and not str(params["imageUrl"]).lower().startswith(
        ("http://", "https://")
    ):
        return "imageUrl 只支持 http/https 地址。本地文件请改用 filePath"

    if local_path:
        if not os.path.isfile(local_path):
            return f"filePath 指向的文件不存在：{local_path}"
        problem = _check_type_size(
            guess_content_type(local_path, params.get("contentType")),
            os.path.getsize(local_path),
            "本地文件",
        )
        if problem:
            return problem

    if params.get("ticketPath") and not os.path.isfile(params["ticketPath"]):
        return f"ticketPath 指向的文件不存在：{params['ticketPath']}"
    return None


def _base_body(params):
    return {k: params[k] for k in ("tableId", "recordId", "fieldName")}


def _save_json(payload, slug, ts, label):
    """落盘并返回路径（失败只提示，不影响主流程）。"""
    serialized = json.dumps(payload, ensure_ascii=False, indent=2)
    out_path = resolve_data_path(slug, ts)
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(serialized)
        print(f"{label}: {out_path} ({len(serialized)} bytes)")
    except OSError as e:
        print(f"Failed to save {label.lower()} to {out_path}: {e}", file=sys.stderr)
    return serialized


def _read_ticket(path):
    """读回上次落盘的上传票据；坏文件当场报错，不猜。"""
    try:
        with open(path, encoding="utf-8") as f:
            ticket = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"读不出 ticketPath 指向的上传票据：{e}", file=sys.stderr)
        sys.exit(1)
    for key in ("uploadId", "url"):
        if not ticket.get(key):
            print(f"上传票据里缺 {key}，请重新用 filePath 跑一次", file=sys.stderr)
            sys.exit(1)
    return ticket


def _sign(params, ts):
    """申请直传地址。返回出参（含 uploadId/url/uploadMethod/requestHeaders/expiresIn）。"""
    body = _base_body(params)
    body.update(
        {
            "filename": params["filename"],
            "contentType": params["contentType"],
            "size": params["size"],
        }
    )
    result = call_api(body)
    if isinstance(result, dict) and result.get("errcode") == 200 and result.get("uploadId"):
        # 先把票据落盘，再动文件：中途断了也有据可查，不用从头签
        _save_json(result, SLUG + "-ticket", ts, "Saved upload ticket")
        print(f"Signed upload URL (PUT expires in {result.get('expiresIn')}s): {result.get('url')}")
    return result


def _finalize(params, upload_id):
    body = _base_body(params)
    body["uploadId"] = upload_id
    if params.get("filename"):
        body["filename"] = params["filename"]
    return call_api(body)


def _upload_then_finalize(params, ticket):
    """把文件直传到预签名地址，成功后再调完成。"""
    problem = put_file(
        ticket["url"],
        ticket.get("uploadMethod"),
        ticket.get("requestHeaders"),
        params["localPath"],
        params["size"],
    )
    if problem:
        print(
            f"文件直传失败：{problem}\n"
            f"上传地址仍然有效的话，用这个续跑（复用同一个 uploadId，不会重复挂附件）：\n"
            f'  {{"tableId":"{params["tableId"]}","recordId":"{params["recordId"]}",'
            f'"fieldName":"{params["fieldName"]}","ticketPath":"<上面 Saved upload ticket 的路径>"}}',
            file=sys.stderr,
        )
        sys.exit(1)
    print("Direct upload done, finalizing...")
    return _finalize(params, ticket["uploadId"])


def summarize(result):
    """打印紧凑摘要：顶层字段 + 追加的那一项附件。"""
    if not isinstance(result, dict):
        print(f"Response type: {type(result).__name__}")
        print(json.dumps(result, ensure_ascii=False)[:500])
        return

    print(f"Top-level keys: {list(result.keys())}")
    for k in ("errcode", "errmsg", "recordId", "fieldName", "uploadId", "uploadMethod", "expiresIn"):
        if k in result and isinstance(result[k], (int, float, bool, str)):
            print(f"  {k}: {result[k]}")
    attachment = result.get("attachment")
    if isinstance(attachment, dict):
        print("\nAttachment:")
        print(json.dumps(attachment, indent=2, ensure_ascii=False))
        print(
            "\nNote: attachment.token 和本次的 uploadId 是同一个值；"
            "presignedUrl 打开是「下载」不是在线预览，且最长约 3 小时过期。"
        )


def run(params, ts):
    """按入参选模式，返回接口出参。"""
    base = _base_body(params)

    if params.get("imageUrl"):
        return call_api(dict(base, imageUrl=params["imageUrl"]))

    if params.get("uploadId"):
        return _finalize(params, params["uploadId"])

    local_path = params.get("filePath") or params.get("imagePath")
    ticket = _read_ticket(params["ticketPath"]) if params.get("ticketPath") else None

    if ticket is not None and not local_path:
        # 文件其实已经传上去了（比如上次 PUT 成功、只有完成那步没跑到），直接收尾
        return _finalize(params, ticket["uploadId"])

    if ticket is None:
        content_type = guess_content_type(local_path, params.get("contentType"))
        size = os.path.getsize(local_path)
        filename = params.get("filename") or os.path.basename(local_path)
        problem = _check_type_size(content_type, size, "本地文件")
        if problem:
            print(problem, file=sys.stderr)
            sys.exit(1)
        params.update({"filename": filename, "contentType": content_type, "size": size})
        ticket = _sign(params, ts)
        if not (isinstance(ticket, dict) and ticket.get("errcode") == 200 and ticket.get("uploadId")):
            return ticket
    else:
        # 续传：复用上次签出的地址与 uploadId，展示名沿用本地文件名
        params.setdefault("filename", os.path.basename(local_path))

    params["localPath"] = local_path
    return _upload_then_finalize(params, ticket)


def main():
    argv = sys.argv[1:]
    inline = "--inline" in argv
    argv = [a for a in argv if a != "--inline"]

    if not argv:
        print(
            "Usage: smart_table.py uploadAttachment "
            '\'{"tableId":"tblXXX","recordId":"recXXX","fieldName":"附件列名","filePath":"./a.mp4"}\' [--inline]',
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
    result = run(params, ts)

    serialized = _save_json(result, SLUG, ts, "Saved full response")

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
