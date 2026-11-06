#!/usr/bin/env python3
"""上传本地图片：申请预签名、PUT 文件、返回公开 URL（有效期 24 小时）。"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

from api_support import invoke_api, normal_response
import call_api as common_api

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
    """通过公共 run 申请预签名，不读取或保存响应缓存。"""
    params = {
        "contentType": content_type,
        "fileExtension": file_extension,
    }
    try:
        status, result, _path, log = invoke_api(
            '/oss/file/presignedPut',
            'linkfox-maidalv-product-tro-detection-presigned-put',
            params,
        )
    except (OSError, ValueError) as exc:
        print(f'预签名申请失败：{exc}', file=sys.stderr)
        sys.exit(1)
    if log:
        print(log, end='', file=sys.stderr)
    if not normal_response(status, result):
        print(f'预签名申请失败：HTTP {status}；{json.dumps(result, ensure_ascii=False)}', file=sys.stderr)
        sys.exit(1)
    if not isinstance(result.get('url'), str) or not result['url'].strip():
        print('预签名响应缺少非空 url', file=sys.stderr)
        sys.exit(1)
    return result["url"]


def upload_file(presigned_url: str, file_path: str, content_type: str):
    """向预签名 OSS 地址 PUT 素材；这是非 LinkFox 业务接口的文件传输。"""
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
                print(f"上传失败，HTTP 状态：{response.status}", file=sys.stderr)
                sys.exit(1)
    except HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        print(f"上传失败：HTTP {e.code}: {e.reason}\n{body}", file=sys.stderr)
        sys.exit(1)
    except URLError as e:
        print(f"上传连接失败：{e.reason}", file=sys.stderr)
        sys.exit(1)


def extract_public_url(presigned_url: str) -> str:
    """去掉签名查询参数，取得公开 URL。"""
    return presigned_url.split("?")[0]


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if '--help' in argv or '-h' in argv:
        print('用法：upload_image.py <本地图片路径>；输出公开图片 URL JSON')
        return
    if not argv:
        print(
            "用法：upload_image.py <本地图片路径>\n"
            "示例：upload_image.py /path/to/product.png",
            file=sys.stderr,
        )
        sys.exit(1)

    file_path = argv[0]

    if not os.path.isfile(file_path):
        print(f"文件不存在：{file_path}", file=sys.stderr)
        sys.exit(1)

    extension = os.path.splitext(file_path)[1].lstrip(".").lower()
    content_type = CONTENT_TYPE_MAP.get(extension)
    if not content_type:
        print(
            f"不支持的图片格式：.{extension}\n"
            f"支持格式：{', '.join(CONTENT_TYPE_MAP.keys())}",
            file=sys.stderr,
        )
        sys.exit(1)

    # 申请预签名；失败直接停止。
    presigned_url = get_presigned_url(content_type, extension)

    # PUT 原始文件字节；失败不能输出成功 URL。
    upload_file(presigned_url, file_path, content_type)

    # 将公开 URL 以 JSON 写入 stdout。
    public_url = extract_public_url(presigned_url)
    print(json.dumps({"url": public_url}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
