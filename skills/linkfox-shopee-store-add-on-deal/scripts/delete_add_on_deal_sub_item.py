#!/usr/bin/env python3
"""
Shopee Store — delete_add_on_deal_sub_item

官方: https://open.shopee.com/documents/v2/v2.add_on_deal.delete_add_on_deal_sub_item?module=111&type=1

入参说明见 references/apis/delete-add-on-deal-sub-item.md。
"""

from __future__ import annotations

import json
import sys

from _add_on_deal_api_runner import run_add_on_deal_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: delete_add_on_deal_sub_item.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    run_add_on_deal_api("delete_add_on_deal_sub_item", params, "delete_add_on_deal_sub_item.py")


if __name__ == "__main__":
    main()
