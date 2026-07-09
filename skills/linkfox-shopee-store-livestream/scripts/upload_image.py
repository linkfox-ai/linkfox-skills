#!/usr/bin/env python3
"""
Shopee Store — upload_image (v2.livestream.upload_image)
官方: https://open.shopee.com/documents/v2/v2.livestream.upload_image?module=125&type=1
"""

from __future__ import annotations

import json
import sys

from _livestream_api_runner import run_livestream_api
from _shopee_livestream_common import emit_result, lf_inline_flag


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: upload_image.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    inline = lf_inline_flag()
    emit_result(run_livestream_api("upload_image", params, "upload_image.py"), inline)


if __name__ == "__main__":
    main()
