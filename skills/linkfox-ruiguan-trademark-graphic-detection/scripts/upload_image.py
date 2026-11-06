#!/usr/bin/env python3
"""上传本地图片，返回有效期 24 小时的公开 URL。

用法：python upload_image.py <local_image_path>
先通过 LinkFox 获取预签名地址，再向对象存储 PUT；stdout 只输出公开 URL JSON。
"""

from contextlib import redirect_stdout
import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

import call_api as api
from call_api import run
from _runtime import output_in_cwd, response_with_status

API_PATH = '/oss/file/presignedPut'
SLUG = 'linkfox-ruiguan-trademark-graphic-detection-upload-image'
CONTENT_TYPE_MAP = {
    'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png',
    'gif': 'image/gif', 'webp': 'image/webp', 'heic': 'image/heic',
}


def _normal_response(status, result):
    if status is None or not 200 <= status < 300 or not isinstance(result, dict):
        return False
    value = result.get('errcode')
    if value is None or isinstance(value, str) and not value.strip():
        return True
    if isinstance(value, str):
        value = value.strip()
        if len(value) != 3 or not value.isascii() or not value.isdigit():
            return False
        value = int(value)
    return type(value) in (int, float) and 200 <= value < 300 and value % 1 == 0


def get_presigned_url(content_type: str, file_extension: str) -> str:
    """通过公共 run 获取地址；不缓存，保存响应，日志写入 stderr。"""
    captured = {}
    transport = api.call_api

    def capture(path, params):
        status, payload = transport(path, params)
        captured.update(status=status, payload=payload)
        # 公共 CLI 预期 JSON 对象；异常数组或标量完整保留在 response 中。
        return status, response_with_status(status, payload)

    api.call_api = capture
    try:
        with output_in_cwd(), redirect_stdout(sys.stderr):
            run(API_PATH, SLUG, argv=[json.dumps({
                'contentType': content_type, 'fileExtension': file_extension,
            }), '--no-cache', '--inline'])
    finally:
        api.call_api = transport

    result = captured['payload']
    if not _normal_response(captured['status'], result):
        print(f"获取预签名地址失败：HTTP {captured['status']}，{json.dumps(result, ensure_ascii=False)}", file=sys.stderr)
        raise SystemExit(1)
    url = result.get('url')
    if not isinstance(url, str) or not url.strip():
        print('获取预签名地址失败：响应缺少有效 url', file=sys.stderr)
        raise SystemExit(1)
    return url


def upload_file(presigned_url: str, file_path: str, content_type: str):
    """向对象存储 PUT 图片；该请求不携带 LinkFox API 密钥。"""
    with open(file_path, "rb") as f:
        file_data = f.read()

    req = Request(
        presigned_url,
        data=file_data,
        headers={
            "Content-Type": content_type,
            "x-oss-object-acl": "public-read",
        },
        method="PUT",
    )

    try:
        with urlopen(req, timeout=120) as response:
            if response.status not in (200, 201):
                print(f"Upload failed with status: {response.status}", file=sys.stderr)
                sys.exit(1)
    except HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        print(f"Upload failed: HTTP {e.code}: {e.reason}\n{body}", file=sys.stderr)
        sys.exit(1)
    except URLError as e:
        print(f"Upload connection failed: {e.reason}", file=sys.stderr)
        sys.exit(1)


def extract_public_url(presigned_url: str) -> str:
    """仅去除查询参数，保留公开 URL 路径和编码。"""
    return presigned_url.split("?")[0]


def main():
    if len(sys.argv) < 2:
        print(
            "Usage: upload_image.py <local_image_path>\n"
            "Example: upload_image.py /path/to/product.png",
            file=sys.stderr,
        )
        sys.exit(1)

    if sys.argv[1] in ('--help', '-h'):
        print(__doc__)
        return

    file_path = sys.argv[1]

    if not os.path.isfile(file_path):
        print(f"File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    extension = os.path.splitext(file_path)[1].lstrip(".").lower()
    content_type = CONTENT_TYPE_MAP.get(extension)
    if not content_type:
        print(
            f"Unsupported image format: .{extension}\n"
            f"Supported formats: {', '.join(CONTENT_TYPE_MAP.keys())}",
            file=sys.stderr,
        )
        sys.exit(1)

    # 获取预签名上传地址
    presigned_url = get_presigned_url(content_type, extension)

    # 上传到对象存储
    upload_file(presigned_url, file_path, content_type)

    # 标准输出为单个公开 URL JSON
    public_url = extract_public_url(presigned_url)
    print(json.dumps({"url": public_url}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
