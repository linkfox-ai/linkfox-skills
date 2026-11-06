#!/usr/bin/env python3
"""
Shopee Store — get_address_list

官方: https://open.shopee.com/documents/v2/v2.logistics.get_address_list?module=95&type=1

入参说明见 references/apis/get-address-list.md。
"""

from __future__ import annotations

import json
import sys

from _logistics_api_runner import run_logistics_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: get_address_list.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    run_logistics_api("get_address_list", params, "get_address_list.py")


if __name__ == "__main__":
    main()
