#!/usr/bin/env python3
"""
Shopee Store — upload_serviceable_polygon

官方: https://open.shopee.com/documents/v2/v2.logistics.upload_serviceable_polygon?module=95&type=1

入参说明见 references/apis/upload-serviceable-polygon.md。
"""

from __future__ import annotations

import json
import sys

from _logistics_api_runner import run_logistics_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: upload_serviceable_polygon.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    run_logistics_api("upload_serviceable_polygon", params, "upload_serviceable_polygon.py")


if __name__ == "__main__":
    main()
