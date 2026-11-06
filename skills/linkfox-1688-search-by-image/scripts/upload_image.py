#!/usr/bin/env python3
"""上传本地图片：通过公共执行器获取凭证，再向 OSS PUT，返回公开链接。"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

import call_api as api
from _linkfox_runner import is_normal_response, run_request

_API_BASE = (os.environ.get("LINKFOX_TOOL_GATEWAY") or "https://tool-gateway.linkfox.com").rstrip("/")

CONTENT_TYPE_MAP = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "gif": "image/gif",
    "webp": "image/webp",
    "heic": "image/heic",
}


def get_presigned_url(content_type: str, file_extension: str) -> str:
    """申请上传凭证；无缓存，标准输出继续保留给最终公开 URL。"""
    try:
        status, result = run_request(
            '/oss/file/presignedPut', 'linkfox-1688-search-by-image-upload',
            {'contentType': content_type, 'fileExtension': file_extension},
            quiet=True,
        )
    except OSError as exc:
        print(f'当前目录保存失败: {exc}', file=sys.stderr)
        sys.exit(1)
    if not is_normal_response(status, result):
        print(f'上传凭证失败: HTTP {status}: {json.dumps(result, ensure_ascii=False)}', file=sys.stderr)
        sys.exit(1)
    if not isinstance(result.get('url'), str) or not result['url'].strip():
        print('上传凭证缺少有效 url', file=sys.stderr)
        sys.exit(1)
    return result['url']


def upload_file(presigned_url: str, file_path: str, content_type: str):
    """向预签名 OSS URL 发送原始文件字节。"""
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
                print(f"上传失败，状态码: {response.status}", file=sys.stderr)
                sys.exit(1)
    except HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        print(f"上传失败: HTTP {e.code}: {e.reason}\n{body}", file=sys.stderr)
        sys.exit(1)
    except URLError as e:
        print(f"上传连接失败: {e.reason}", file=sys.stderr)
        sys.exit(1)


def extract_public_url(presigned_url: str) -> str:
    """去掉签名查询参数得到公开图片链接。"""
    return presigned_url.split("?")[0]


def main():
    if len(sys.argv) > 1 and sys.argv[1] in ('--help', '-h'):
        print('用法: upload_image.py <本地图片路径>')
        return
    if len(sys.argv) < 2:
        print(
            "用法: upload_image.py <本地图片路径>\n"
            "示例: upload_image.py /path/to/product.png",
            file=sys.stderr,
        )
        sys.exit(1)

    file_path = sys.argv[1]

    if not os.path.isfile(file_path):
        print(f"文件不存在: {file_path}", file=sys.stderr)
        sys.exit(1)

    extension = os.path.splitext(file_path)[1].lstrip(".").lower()
    content_type = CONTENT_TYPE_MAP.get(extension)
    if not content_type:
        print(
            f"不支持的图片格式: .{extension}\n"
            f"支持的格式: {', '.join(CONTENT_TYPE_MAP.keys())}",
            file=sys.stderr,
        )
        sys.exit(1)

    # 第一步：获取上传凭证
    presigned_url = get_presigned_url(content_type, extension)

    # 第二步：上传文件
    upload_file(presigned_url, file_path, content_type)

    # 第三步：输出公开链接
    public_url = extract_public_url(presigned_url)
    print(json.dumps({"url": public_url}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
