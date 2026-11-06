#!/usr/bin/env python3
"""本地图片上传：公共 run 取得预签名地址，OSS PUT 后输出公开 URL。"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from _image_runtime import run_request, is_normal_response

API_PATH = "/oss/file/presignedPut"
SLUG = "linkfox-multimodal-recognize-image-presigned-put"

CONTENT_TYPE_MAP = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "gif": "image/gif",
    "webp": "image/webp",
    "heic": "image/heic",
}


def get_presigned_url(content_type: str, file_extension: str) -> str:
    """通过公共调用器取得签名，不缓存有时效的 URL。"""
    try:
        status, result = run_request(API_PATH, SLUG, {
            "contentType": content_type,
            "fileExtension": file_extension,
        }, quiet=True)
    except OSError as e:
        print(f"无法保存预签名响应: {e}", file=sys.stderr)
        sys.exit(1)
    if not is_normal_response(status, result):
        print(f"获取预签名失败，HTTP {status}: {json.dumps(result, ensure_ascii=False)}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(result.get("url"), str) or not result["url"].strip():
        print("预签名响应缺少有效 url", file=sys.stderr)
        sys.exit(1)

    return result["url"]


def upload_file(presigned_url: str, file_path: str, content_type: str):
    """上传原始文件至返回的 OSS URL；不发送 LinkFox 密钥。"""
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
    """去除签名查询串得到公开 URL。"""
    return presigned_url.split("?")[0]


def main():
    if "--help" in sys.argv[1:] or "-h" in sys.argv[1:]:
        print("用法: upload_image.py <本地图片路径>")
        return
    if len(sys.argv) != 2:
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
            f"不支持的上传格式: .{extension}\n"
            f"支持格式: {', '.join(CONTENT_TYPE_MAP.keys())}",
            file=sys.stderr,
        )
        sys.exit(1)

    # 1. 获取预签名地址
    presigned_url = get_presigned_url(content_type, extension)

    # 2. 上传素材至 OSS
    try:
        upload_file(presigned_url, file_path, content_type)
    except OSError as e:
        print(f"读取本地文件失败: {e}", file=sys.stderr)
        sys.exit(1)

    # 3. 保留仅公开 URL JSON 的标准输出
    public_url = extract_public_url(presigned_url)
    print(json.dumps({"url": public_url}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
