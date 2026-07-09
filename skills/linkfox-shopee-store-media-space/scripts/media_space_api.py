#!/usr/bin/env python3
"""
Shopee Store — generic MediaSpace API caller
==============================================

Usage:
  python media_space_api.py '{"api": "init_video_upload", "shopId": "67890", "body": {...}}'

Official docs: https://open.shopee.com/documents/v2/v2.media_space.<api>?module=91&type=1
"""

from __future__ import annotations

import json
import sys

from _media_space_api_runner import run_media_space_api
from _media_space_endpoints import list_api_names
from _shopee_media_space_common import emit_result, lf_inline_flag


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: media_space_api.py '<JSON with api field>'\nAvailable: {', '.join(list_api_names())}", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    if not params.get("api"):
        print("Missing required field: api", file=sys.stderr)
        sys.exit(1)
    inline = lf_inline_flag()
    emit_result(run_media_space_api(str(params["api"]), params, "media_space_api.py"), inline)


if __name__ == "__main__":
    main()
