#!/usr/bin/env python3
"""
Shopee Store — get_unbind_order_list

官方: https://open.shopee.com/documents/v2/v2.first_mile.get_unbind_order_list?module=96&type=1

入参说明见 references/apis/get-unbind-order-list.md。
"""

from __future__ import annotations

import json
import sys

from _first_mile_api_runner import run_first_mile_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: get_unbind_order_list.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    run_first_mile_api("get_unbind_order_list", params, "get_unbind_order_list.py")


if __name__ == "__main__":
    main()
