#!/usr/bin/env python3
"""
Shopee Store — generic Media API caller
========================================

Usage:
  python media_api.py '{"api": "upload_image", "shopId": "67890", "body": {...}}'

Official docs: https://open.shopee.com/documents/v2/v2.media.<api>?module=130&type=1
"""

from __future__ import annotations

import json
import sys

from _media_api_runner import run_media_api
from _media_endpoints import list_api_names


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: media_api.py '<JSON with api field>'\nAvailable: {', '.join(list_api_names())}", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    if not params.get("api"):
        print("Missing required field: api", file=sys.stderr)
        sys.exit(1)
    run_media_api(str(params["api"]), params, "media_api.py")


if __name__ == "__main__":
    main()
