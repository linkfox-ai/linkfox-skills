#!/usr/bin/env python3
"""上传本地图片：公共调用器申请预签名，OSS PUT 上传后返回公开链接。"""

import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from _patent_runtime import is_normal_response, run_request

API_PATH = "/oss/file/presignedPut"
CONTENT_TYPE_MAP = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "gif": "image/gif",
    "webp": "image/webp",
    "heic": "image/heic",
}


def get_presigned_url(content_type: str, file_extension: str) -> str:
    """公共调用器负责 LinkFox POST、认证与响应落盘，不缓存预签名。"""
    status, result = run_request(
        API_PATH,
        "upload-presign",
        {"contentType": content_type, "fileExtension": file_extension},
        quiet=True,
    )
    if not is_normal_response(status, result):
        print(f"申请预签名失败（HTTP {status}）: {json.dumps(result, ensure_ascii=False)}", file=sys.stderr)
        raise SystemExit(1)
    url = result.get("url")
    if not isinstance(url, str) or not url.strip():
        print("申请预签名失败：响应缺少有效 url", file=sys.stderr)
        raise SystemExit(1)
    return url


def upload_file(presigned_url: str, file_path: str, content_type: str):
    """只向预签名 OSS 地址上传文件，不向该地址发送 LinkFox API Key。"""
    with open(file_path, "rb") as handle:
        file_data = handle.read()
    request = Request(
        presigned_url,
        data=file_data,
        headers={"Content-Type": content_type, "x-oss-object-acl": "public-read"},
        method="PUT",
    )
    try:
        with urlopen(request, timeout=120) as response:
            if response.status not in (200, 201):
                print(f"上传失败，HTTP 状态码: {response.status}", file=sys.stderr)
                raise SystemExit(1)
    except HTTPError as exc:
        body = exc.read().decode("utf-8") if exc.fp else ""
        print(f"上传失败: HTTP {exc.code}: {exc.reason}\n{body}", file=sys.stderr)
        raise SystemExit(1)
    except URLError as exc:
        print(f"上传连接失败: {exc.reason}", file=sys.stderr)
        raise SystemExit(1)


def extract_public_url(presigned_url: str) -> str:
    """去掉预签名 URL 的查询串，得到公开图片链接。"""
    return presigned_url.split("?")[0]


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("--help", "-h"):
        print("用法: upload_image.py <本地图片路径>", file=sys.stdout if argv else sys.stderr)
        return 0 if argv else 1
    file_path = argv[0]
    if not os.path.isfile(file_path):
        print(f"文件不存在: {file_path}", file=sys.stderr)
        return 1
    extension = os.path.splitext(file_path)[1].lstrip(".").lower()
    content_type = CONTENT_TYPE_MAP.get(extension)
    if not content_type:
        print(f"不支持图片格式: .{extension}；支持: {', '.join(CONTENT_TYPE_MAP)}", file=sys.stderr)
        return 1
    try:
        presigned_url = get_presigned_url(content_type, extension)
        upload_file(presigned_url, file_path, content_type)
    except OSError as exc:
        print(f"无法读取文件或保存完整响应: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"url": extract_public_url(presigned_url)}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
