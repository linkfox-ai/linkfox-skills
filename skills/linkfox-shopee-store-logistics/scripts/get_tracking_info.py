#!/usr/bin/env python3
"""
Shopee Store — get_tracking_info

官方: https://open.shopee.com/documents/v2/v2.logistics.get_tracking_info?module=95&type=1

入参说明见 references/apis/get-tracking-info.md。
"""

from __future__ import annotations

import json
import sys

from _logistics_api_runner import run_logistics_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: get_tracking_info.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    run_logistics_api("get_tracking_info", params, "get_tracking_info.py")


if __name__ == "__main__":
    main()
