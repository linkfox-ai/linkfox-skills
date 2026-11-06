#!/usr/bin/env python3
"""上传本地图片：获取预签名 PUT 地址，上传 OSS，输出去掉查询串的公开 URL。"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

from patent_runtime import run_gateway, normal_response

CONTENT_TYPE_MAP = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "gif": "image/gif",
    "webp": "image/webp",
    "heic": "image/heic",
}


def get_presigned_url(content_type: str, file_extension: str) -> str:
    """经公共调用器获取预签名地址；不缓存，stdout 只保留最终公开 URL。"""
    try:
        status, result = run_gateway(
            "/oss/file/presignedPut",
            "linkfox-zhihuiya-patent-image-search-upload",
            {"contentType": content_type, "fileExtension": file_extension},
            quiet=True,
        )
    except OSError as exc:
        print(f"当前目录数据保存失败: {exc}", file=sys.stderr)
        sys.exit(1)
    if not normal_response(status, result):
        print(f"获取预签名地址失败: HTTP {status}: "
              f"{json.dumps(result, ensure_ascii=False)}", file=sys.stderr)
        sys.exit(1)
    url = result.get("url")
    if not isinstance(url, str) or not url:
        print("预签名响应缺少 url。", file=sys.stderr)
        sys.exit(1)
    return url


def upload_file(presigned_url: str, file_path: str, content_type: str):
    """向预签名 OSS 地址上传文件，保留公开读 ACL；此 PUT 不调用 LinkFox 网关。"""
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
    """移除签名查询串，得到公开 URL；有效期为 24 小时。"""
    return presigned_url.split("?")[0]


def main():
    if len(sys.argv) == 2 and sys.argv[1] in ("--help", "-h"):
        print("用法: upload_image.py <本地图片路径>")
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
            f"支持格式: {', '.join(CONTENT_TYPE_MAP.keys())}",
            file=sys.stderr,
        )
        sys.exit(1)

    # 1. 获取预签名地址
    presigned_url = get_presigned_url(content_type, extension)

    # 2. 向 OSS 上传文件
    upload_file(presigned_url, file_path, content_type)

    # 3. 输出公开 URL
    public_url = extract_public_url(presigned_url)
    print(json.dumps({"url": public_url}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
