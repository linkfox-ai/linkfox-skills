#!/usr/bin/env python3
"""
Shopee Store — get_add_on_deal_main_item

官方: https://open.shopee.com/documents/v2/v2.add_on_deal.get_add_on_deal_main_item?module=111&type=1

入参说明见 references/apis/get-add-on-deal-main-item.md。
"""

from __future__ import annotations

import json
import sys

from _add_on_deal_api_runner import run_add_on_deal_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: get_add_on_deal_main_item.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    run_add_on_deal_api("get_add_on_deal_main_item", params, "get_add_on_deal_main_item.py")


if __name__ == "__main__":
    main()
