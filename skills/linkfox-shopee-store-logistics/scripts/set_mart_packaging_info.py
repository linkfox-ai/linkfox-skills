#!/usr/bin/env python3
"""
Shopee Store — set_mart_packaging_info

官方: https://open.shopee.com/documents/v2/v2.logistics.set_mart_packaging_info?module=95&type=1

入参说明见 references/apis/set-mart-packaging-info.md。
"""

from __future__ import annotations

import json
import sys

from _logistics_api_runner import run_logistics_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: set_mart_packaging_info.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    run_logistics_api("set_mart_packaging_info", params, "set_mart_packaging_info.py")


if __name__ == "__main__":
    main()
