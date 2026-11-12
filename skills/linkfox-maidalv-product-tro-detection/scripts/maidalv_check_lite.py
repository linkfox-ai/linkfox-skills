#!/usr/bin/env python3
"""卖大律 POD 图片检测；通过公共调用器同步查询候选 IP。"""

import base64
import binascii
import sys
from urllib.parse import urlparse

from pod_api_support import run_detection

API_PATH = '/maidalv/checkLite'
SLUG = 'linkfox-maidalv-product-tro-detection'
OUTPUT_SLUG = SLUG + '-check-lite'
MAX_IMAGE_BYTES = 10 * 1024 * 1024


def validate_params(params):
    unknown = set(params) - {'mainProductImage', 'description', 'language'}
    if unknown:
        raise ValueError(f'POD 图片检测不支持字段：{", ".join(sorted(unknown))}')
    image = params.get('mainProductImage')
    if not isinstance(image, str) or not image.strip():
        raise ValueError('mainProductImage 必须为非空图片 URL、data URI 或纯 Base64')
    if 'description' in params and not isinstance(params['description'], str):
        raise ValueError('description 必须为字符串')
    if 'language' in params and params['language'] not in ('zh', 'en'):
        raise ValueError('language 仅支持 zh 或 en')
    parsed = urlparse(image)
    if parsed.scheme in ('http', 'https') and parsed.netloc:
        return  # 不额外下载 URL，实际格式和大小由服务端校验。
    encoded = image
    if image.startswith('data:'):
        header, separator, encoded = image.partition(',')
        if not separator or header.lower() not in (
            'data:image/jpeg;base64', 'data:image/png;base64',
            'data:image/webp;base64', 'data:image/gif;base64',
        ):
            raise ValueError('POD data URI 仅支持 JPEG、PNG、WEBP、GIF 的 Base64')
    if len(encoded) > ((MAX_IMAGE_BYTES + 2) // 3) * 4:
        raise ValueError('图片不能超过 10 MB')
    try:
        data = base64.b64decode(encoded, validate=True)
    except (ValueError, binascii.Error):
        raise ValueError('mainProductImage 不是有效图片 URL 或 Base64') from None
    if not data or len(data) > MAX_IMAGE_BYTES:
        raise ValueError('图片必须非空且不超过 10 MB')
    supported = (data.startswith(b'\xff\xd8\xff') or data.startswith(b'\x89PNG\r\n\x1a\n')
                 or data.startswith((b'GIF87a', b'GIF89a'))
                 or (data.startswith(b'RIFF') and data[8:12] == b'WEBP'))
    if not supported:
        raise ValueError('POD 图片仅支持 JPEG、PNG、WEBP、GIF')


def main(argv=None):
    return run_detection(API_PATH, OUTPUT_SLUG, 'lite', argv, validate_params)


if __name__ == '__main__':
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    sys.exit(main())
