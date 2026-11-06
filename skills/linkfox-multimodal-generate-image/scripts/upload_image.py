#!/usr/bin/env python3
"""上传本地参考图：申请预签名、上传素材并输出公开图片 URL。"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

import _image_gateway

API_PATH = "/oss/file/presignedPut"
SLUG = "linkfox-multimodal-generate-image-upload"

CONTENT_TYPE_MAP = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "gif": "image/gif",
    "webp": "image/webp",
    "heic": "image/heic",
}


def _normal_response(http_status, result):
    """按公共规则判断响应；0 与 false 不视为空。"""
    if http_status is None or not 200 <= http_status < 300 or not isinstance(result, dict):
        return False
    code = result.get("errcode")
    if code is None:
        return True
    if isinstance(code, str):
        code = code.strip()
        if not code:
            return True
        if len(code) != 3 or not code.isascii() or not code.isdigit():
            return False
        code = int(code)
    return type(code) in (int, float) and 200 <= code < 300 and code % 1 == 0


def get_presigned_url(content_type: str, file_extension: str) -> str:
    """通过公共 run 获取预签名；该操作始终关闭缓存。"""
    status, result = _image_gateway.run(
        API_PATH, SLUG,
        {"contentType": content_type, "fileExtension": file_extension},
        inline=True, quiet=True,
    )
    if not _normal_response(status, result):
        print(f"获取预签名失败，HTTP {status}: {json.dumps(result, ensure_ascii=False)}", file=sys.stderr)
        raise SystemExit(1)
    url = result.get("url")
    if not isinstance(url, str) or not url.strip():
        print("预签名响应缺少有效 url", file=sys.stderr)
        raise SystemExit(1)
    return url


def upload_file(presigned_url: str, file_path: str, content_type: str):
    """向素材存储地址 PUT 原始图片，不发送 LinkFox API Key。"""
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
    """去掉签名查询串，得到公开图片地址。"""
    return presigned_url.split("?")[0]


def main():
    if sys.argv[1:] in (["--help"], ["-h"]):
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
            f"支持的格式: {', '.join(CONTENT_TYPE_MAP.keys())}",
            file=sys.stderr,
        )
        sys.exit(1)

    # 1. 获取预签名
    presigned_url = get_presigned_url(content_type, extension)

    # 2. 上传素材
    upload_file(presigned_url, file_path, content_type)

    # 3. 输出公开 URL
    public_url = extract_public_url(presigned_url)
    print(json.dumps({"url": public_url}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
