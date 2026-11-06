#!/usr/bin/env python3
"""通过 LinkFox 预签名 PUT 流程上传一张本地图片。

用法：
  python upload_image.py /path/to/product.jpg

输出包含公开 OSS 地址与检测所得 MIME 类型的 JSON。
不打印 API Key 或预签名上传地址的私密查询参数。
"""

import json
import os
import sys
import re
from _linkfox_transport import request, is_success
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, urlunsplit
from urllib.request import Request, urlopen

PRESIGN_PATH = "/oss/file/presignedPut"
MAX_IMAGE_BYTES = 10_000_000
CONTENT_TYPE_MAP = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "gif": "image/gif",
    "webp": "image/webp",
    "bmp": "image/bmp",
}


def _detect_content_type(header):
    if header.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if header.startswith(b"GIF8"):
        return "image/gif"
    if len(header) >= 12 and header[:4] == b"RIFF" and header[8:12] == b"WEBP":
        return "image/webp"
    if header.startswith(b"BM"):
        return "image/bmp"
    return None


def _validate_local_image(local_path, expected_content_type):
    size = os.path.getsize(local_path)
    if size <= 0:
        raise RuntimeError("Image file is empty")
    if size > MAX_IMAGE_BYTES:
        raise RuntimeError("Image file exceeds the 10 MB limit")
    with open(local_path, "rb") as file:
        detected_content_type = _detect_content_type(file.read(12))
    if detected_content_type is None:
        raise RuntimeError("Image bytes must be JPEG, PNG, GIF, WebP, or BMP")
    if detected_content_type != expected_content_type:
        raise RuntimeError(
            "Image extension does not match the actual image byte format"
        )


def _api_key():
    key = os.environ.get("LINKFOX_AGENT_API_KEY") or os.environ.get("LINKFOXAGENT_API_KEY")
    if not key:
        raise RuntimeError("API Key not configured; set LINKFOX_AGENT_API_KEY or LINKFOXAGENT_API_KEY first")
    return key


def _safe_message(message):
    """错误消息也不能泄露签名查询参数或密钥。"""
    text = str(message)
    for key in (os.environ.get("LINKFOX_AGENT_API_KEY"), os.environ.get("LINKFOXAGENT_API_KEY")):
        if key:
            text = text.replace(key, "[REDACTED]")
    return re.sub(r"https?://[^\s<>\"']+", lambda match: match.group(0).split("?", 1)[0].split("#", 1)[0], text)


def _presigned_url(content_type, extension):
    _api_key()  # 缺少密钥时通过 JSON 错误与退出码报告失败。
    status, result = request(PRESIGN_PATH, "linkfox-geekbi-temu-search-by-image-upload",
                             {"contentType": content_type, "fileExtension": extension})
    if not is_success(status, result):
        message = (result.get("errmsg") or result.get("error") or "unknown error") if isinstance(result, dict) else "unknown error"
        if status is not None and not 200 <= status < 300:
            message = f"HTTP {status}: {message}"
        raise RuntimeError(f"Unable to obtain upload URL: {_safe_message(message)}")
    url = result.get("url")
    try:
        parts = urlsplit(url) if isinstance(url, str) else None
        valid_url = parts and parts.scheme == "https" and parts.hostname
    except ValueError:
        valid_url = False
    if not valid_url:
        raise RuntimeError("Upload service response is missing a valid HTTPS URL")
    return url


def _upload(presigned_url, local_path, content_type):
    with open(local_path, "rb") as file:
        payload = file.read()
    req = Request(
        presigned_url,
        data=payload,
        headers={
            "Content-Type": content_type,
            "x-oss-object-acl": "public-read",
        },
        method="PUT",
    )
    try:
        with urlopen(req, timeout=120) as response:
            if response.status not in (200, 201):
                raise RuntimeError(f"Image upload failed with HTTP {response.status}")
    except HTTPError as exc:
        raise RuntimeError(f"Image upload failed with HTTP {exc.code}") from None
    except URLError as exc:
        raise RuntimeError(f"Image upload failed: {_safe_message(exc.reason)}") from None


def _public_url(presigned_url):
    parts = urlsplit(presigned_url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def main():
    if len(sys.argv) != 2:
        print("Usage: upload_image.py <local-image-path>", file=sys.stderr)
        sys.exit(1)

    local_path = os.path.abspath(sys.argv[1])
    if not os.path.isfile(local_path):
        print(json.dumps({"error": f"File not found: {local_path}"}, ensure_ascii=False))
        sys.exit(1)

    extension = os.path.splitext(local_path)[1].lstrip(".").lower()
    content_type = CONTENT_TYPE_MAP.get(extension)
    if not content_type:
        supported = ", ".join(sorted(CONTENT_TYPE_MAP))
        print(
            json.dumps(
                {
                    "error": f"Unsupported image format: .{extension}",
                    "supported": supported,
                },
                ensure_ascii=False,
            )
        )
        sys.exit(1)

    try:
        _validate_local_image(local_path, content_type)
        presigned_url = _presigned_url(content_type, extension)
        _upload(presigned_url, local_path, content_type)
        public_url = _public_url(presigned_url)
    except (OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"error": _safe_message(exc)}, ensure_ascii=False))
        sys.exit(1)

    print(
        json.dumps(
            {
                "url": public_url,
                "contentType": content_type,
                "path": urlsplit(public_url).path.lstrip("/"),
                "name": os.path.basename(local_path),
                "size": os.path.getsize(local_path),
                "ext": extension,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
