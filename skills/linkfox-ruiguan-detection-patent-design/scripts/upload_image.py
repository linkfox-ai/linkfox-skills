#!/usr/bin/env python3
"""上传本地图片：获取预签名、OSS PUT，再输出公开图片链接。

用法：python upload_image.py <本地图片路径>
公开链接有效 24 小时；stdout 输出 {"url": "..."}。
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

from _ruiguan_common import run_gateway, is_normal_response
from call_api import get_api_key

API_PATH = '/oss/file/presignedPut'
SLUG = 'linkfox-ruiguan-detection-patent-design-upload'
CONTENT_TYPE_MAP = {
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'gif': 'image/gif',
    'webp': 'image/webp',
    'heic': 'image/heic',
}


def get_presigned_url(content_type: str, file_extension: str) -> str:
    """通过公共调用器请求预签名，不读取或写入响应缓存。"""
    try:
        status, result, _ = run_gateway(API_PATH, SLUG, {
            'contentType': content_type,
            'fileExtension': file_extension,
        })
    except OSError as exc:
        print(f'无法保存预签名响应：{exc}', file=sys.stderr)
        raise SystemExit(1)
    if not is_normal_response(status, result):
        print(f'获取预签名失败：HTTP {status}，{json.dumps(result, ensure_ascii=False)}', file=sys.stderr)
        raise SystemExit(1)
    url = result.get('url')
    if not isinstance(url, str) or not url.strip():
        print('预签名响应缺少有效 url', file=sys.stderr)
        raise SystemExit(1)
    return url


def upload_file(presigned_url: str, file_path: str, content_type: str):
    """仅对预签名存储地址执行 PUT，保留原始查询串和编码。"""
    with open(file_path, 'rb') as stream:
        file_data = stream.read()
    req = Request(presigned_url, data=file_data, headers={
        'Content-Type': content_type,
        'x-oss-object-acl': 'public-read',
    }, method='PUT')
    try:
        with urlopen(req, timeout=120) as response:
            if response.status not in (200, 201):
                print(f'图片上传失败，状态码：{response.status}', file=sys.stderr)
                raise SystemExit(1)
    except HTTPError as exc:
        body = exc.read().decode('utf-8') if exc.fp else ''
        print(f'图片上传失败：HTTP {exc.code}: {exc.reason}\n{body}', file=sys.stderr)
        raise SystemExit(1)
    except URLError as exc:
        print(f'图片上传连接失败：{exc.reason}', file=sys.stderr)
        raise SystemExit(1)


def extract_public_url(presigned_url: str) -> str:
    """仅移除签名查询串，不解码或重建对象路径。"""
    return presigned_url.split('?')[0]


def main():
    if len(sys.argv) < 2:
        print('用法：upload_image.py <本地图片路径>', file=sys.stderr)
        raise SystemExit(1)
    file_path = sys.argv[1]
    if not os.path.isfile(file_path):
        print(f'文件不存在：{file_path}', file=sys.stderr)
        raise SystemExit(1)
    extension = os.path.splitext(file_path)[1].lstrip('.').lower()
    content_type = CONTENT_TYPE_MAP.get(extension)
    if not content_type:
        print(f'不支持的图片格式：.{extension}；支持：{", ".join(CONTENT_TYPE_MAP)}', file=sys.stderr)
        raise SystemExit(1)
    presigned_url = get_presigned_url(content_type, extension)
    upload_file(presigned_url, file_path, content_type)
    print(json.dumps({'url': extract_public_url(presigned_url)}, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
