#!/usr/bin/env python3
"""
上传本地图片 - LinkFox 技能
将本地图片上传到 OSS，返回公开可访问的图片链接。

步骤:
  1. 通过 LinkFox 公共调用器获取预签名 PUT 地址
  2. 向预签名地址上传本地文件
  3. 返回公开链接（有效期 24 小时）

用法:
  python upload_image.py /path/to/local/image.png
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
import time
from _api_runner import run_response, is_normal_response
from amazon_search_by_image import resolve_data_path

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
    """通过公共 run 获取预签名地址；每次上传均不使用缓存。"""
    output_path = resolve_data_path("linkfox-amazon-search-by-image-upload", time.time())
    status, result = run_response(
        "/oss/file/presignedPut", "linkfox-amazon-search-by-image-upload",
        {"contentType": content_type, "fileExtension": file_extension}, output_path,
    )
    if not is_normal_response(status, result):
        print(f"获取上传地址失败: HTTP {status}: {json.dumps(result, ensure_ascii=False)}", file=sys.stderr)
        sys.exit(1)
    url = result.get("url") if isinstance(result, dict) else None
    if not isinstance(url, str) or not url.strip():
        print("获取上传地址失败: 响应缺少非空 url", file=sys.stderr)
        sys.exit(1)
    return url


def upload_file(presigned_url: str, file_path: str, content_type: str):
    """向预签名 OSS 地址 PUT 图片；此处不是 LinkFox 网关调用。"""
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
    """移除签名查询串，取得公开图片链接。"""
    return presigned_url.split("?")[0]


def main():
    if len(sys.argv) < 2:
        print(
            "用法: upload_image.py <local_image_path>\n"
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
            f"支持格式: {', '.join(CONTENT_TYPE_MAP.keys())}",
            file=sys.stderr,
        )
        sys.exit(1)

    # 第一步：获取预签名地址
    presigned_url = get_presigned_url(content_type, extension)

    # 第二步：上传文件
    upload_file(presigned_url, file_path, content_type)

    # 第三步：输出公开链接
    public_url = extract_public_url(presigned_url)
    print(json.dumps({"url": public_url}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
