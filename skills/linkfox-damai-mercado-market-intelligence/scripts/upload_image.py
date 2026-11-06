#!/usr/bin/env python3
"""本地图片上传：公共调用器获取预签名，OSS PUT 后仅输出公开 URL。"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

import call_api as api
from damai_mercado_market_intelligence import run_request

PRESIGN_PATH = "/oss/file/presignedPut"
CONTENT_TYPE_MAP = {
    "jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
    "gif": "image/gif", "webp": "image/webp", "heic": "image/heic",
}


def get_presigned_url(content_type: str, file_extension: str) -> str:
    status, result = run_request(
        PRESIGN_PATH, "linkfox-damai-mercado-market-intelligence-upload",
        {"contentType": content_type, "fileExtension": file_extension},
        quiet=True, use_cache=False,
    )
    if not (status is not None and 200 <= status < 300 and api._is_cacheable(200, result)):
        print("获取图片上传地址失败，请按接口参考检查认证、用量或网关状态。", file=sys.stderr)
        raise SystemExit(1)
    url = result.get("url")
    if not isinstance(url, str) or not url.startswith(("https://", "http://")):
        print("图片上传地址缺失或无效。", file=sys.stderr)
        raise SystemExit(1)
    return url


def upload_file(presigned_url: str, file_path: str, content_type: str):
    """仅此处直连 OSS 素材 PUT；不转发 LinkFox 凭证或会话头。"""
    with open(file_path, "rb") as stream:
        file_data = stream.read()
    request = Request(presigned_url, data=file_data, method="PUT", headers={
        "Content-Type": content_type,
        "x-oss-object-acl": "public-read",
    })
    try:
        with urlopen(request, timeout=150) as response:
            if response.status not in (200, 201):
                print(f"图片上传失败，HTTP {response.status}。", file=sys.stderr)
                raise SystemExit(1)
    except HTTPError as exc:
        print(f"图片上传失败，HTTP {exc.code}。", file=sys.stderr)
        raise SystemExit(1)
    except URLError:
        print("图片上传连接失败。", file=sys.stderr)
        raise SystemExit(1)


def extract_public_url(presigned_url: str) -> str:
    return presigned_url.split("?", 1)[0]


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv in (["--help"], ["-h"]):
        print("用法：upload_image.py <local_image_path>", file=sys.stdout if argv else sys.stderr)
        return 0 if argv else 1
    if len(argv) != 1:
        print("请提供一个本地图片路径。", file=sys.stderr)
        return 1
    file_path = argv[0]
    if not os.path.isfile(file_path):
        print(f"文件不存在：{file_path}", file=sys.stderr)
        return 1
    extension = os.path.splitext(file_path)[1].lstrip(".").lower()
    content_type = CONTENT_TYPE_MAP.get(extension)
    if not content_type:
        print(f"不支持的图片格式：.{extension}；支持 {', '.join(CONTENT_TYPE_MAP)}。", file=sys.stderr)
        return 1
    try:
        presigned_url = get_presigned_url(content_type, extension)
        upload_file(presigned_url, file_path, content_type)
    except OSError:
        print("图片读取或会话数据保存失败。", file=sys.stderr)
        return 1
    print(json.dumps({"url": extract_public_url(presigned_url)}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
