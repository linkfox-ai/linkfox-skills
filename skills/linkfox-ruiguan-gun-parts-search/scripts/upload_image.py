#!/usr/bin/env python3
"""先通过 LinkFox 公共调用器取签名，再 PUT 本地图片并输出公开 URL。"""

import argparse
import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit

from _ruiguan_common import is_normal_response, run_request

API_PATH = "/oss/file/presignedPut"
SLUG = "linkfox-ruiguan-gun-parts-search-presigned-put"
CONTENT_TYPE_MAP = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "gif": "image/gif",
    "webp": "image/webp",
    "heic": "image/heic",
}


def get_presigned_url(content_type: str, file_extension: str) -> str:
    """签名不缓存；stdout 仅输出最终公开链接。"""
    status, result = run_request(
        API_PATH, SLUG,
        {"contentType": content_type, "fileExtension": file_extension},
        output=sys.stderr,
    )
    if not is_normal_response(status, result):
        print(f"获取预签名失败：HTTP {status}；{json.dumps(result, ensure_ascii=False)}", file=sys.stderr)
        raise SystemExit(1)
    url = result.get("url")
    try:
        parsed = urlsplit(url) if isinstance(url, str) else None
    except ValueError:
        parsed = None
    if not parsed or parsed.scheme not in ("http", "https") or not parsed.netloc:
        print("获取预签名失败：响应缺少有效的 url", file=sys.stderr)
        raise SystemExit(1)
    return url


def upload_file(presigned_url: str, file_path: str, content_type: str):
    """向返回的 OSS 签名地址上传二进制文件，不携带 LinkFox API Key。"""
    with open(file_path, "rb") as f:
        file_data = f.read()
    req = Request(
        presigned_url,
        data=file_data,
        headers={"Content-Type": content_type, "x-oss-object-acl": "public-read"},
        method="PUT",
    )
    try:
        with urlopen(req, timeout=120) as response:
            if response.status not in (200, 201):
                print(f"上传失败：HTTP {response.status}", file=sys.stderr)
                raise SystemExit(1)
    except HTTPError as exc:
        body = exc.read().decode("utf-8") if exc.fp else ""
        print(f"上传失败：HTTP {exc.code}: {exc.reason}\n{body}", file=sys.stderr)
        raise SystemExit(1)
    except URLError as exc:
        print(f"上传连接失败：{exc.reason}", file=sys.stderr)
        raise SystemExit(1)


def extract_public_url(presigned_url: str) -> str:
    """只去掉查询参数，不解码已编码的对象路径。"""
    return presigned_url.split("?")[0]


def main(argv=None):
    parser = argparse.ArgumentParser(description="上传本地图片并返回公开 URL（有效 24 小时）")
    parser.add_argument("local_image_path", help="本地图片路径")
    args = parser.parse_args(argv)
    file_path = args.local_image_path
    if not os.path.isfile(file_path):
        parser.exit(1, f"文件不存在：{file_path}\n")
    extension = os.path.splitext(file_path)[1].lstrip(".").lower()
    content_type = CONTENT_TYPE_MAP.get(extension)
    if not content_type:
        parser.exit(1, f"不支持的图片格式：.{extension}；支持：{', '.join(CONTENT_TYPE_MAP)}\n")
    try:
        presigned_url = get_presigned_url(content_type, extension)
        upload_file(presigned_url, file_path, content_type)
    except OSError as exc:
        parser.exit(1, f"文件或会话数据处理失败：{exc}\n")
    print(json.dumps({"url": extract_public_url(presigned_url)}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
