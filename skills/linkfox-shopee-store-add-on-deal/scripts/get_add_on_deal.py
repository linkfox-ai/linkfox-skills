#!/usr/bin/env python3
"""
Shopee Store — get_add_on_deal

官方: https://open.shopee.com/documents/v2/v2.add_on_deal.get_add_on_deal?module=111&type=1

入参说明见 references/apis/get-add-on-deal.md。
"""

from __future__ import annotations

import json
import sys

from _add_on_deal_api_runner import run_add_on_deal_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: get_add_on_deal.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    run_add_on_deal_api("get_add_on_deal", params, "get_add_on_deal.py")


if __name__ == "__main__":
    main()
