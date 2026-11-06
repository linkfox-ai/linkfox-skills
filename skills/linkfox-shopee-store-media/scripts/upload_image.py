#!/usr/bin/env python3
"""
Shopee Store — upload_image

官方: https://open.shopee.com/documents/v2/v2.media.upload_image?module=130&type=1

入参说明见 references/apis/upload-image.md。
"""

from __future__ import annotations

import json
import sys

from _media_api_runner import run_media_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: upload_image.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    run_media_api("upload_image", params, "upload_image.py")


if __name__ == "__main__":
    main()
