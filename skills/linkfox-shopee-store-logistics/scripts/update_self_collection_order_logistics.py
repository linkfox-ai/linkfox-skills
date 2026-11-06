#!/usr/bin/env python3
"""
Shopee Store — update_self_collection_order_logistics

官方: https://open.shopee.com/documents/v2/v2.logistics.update_self_collection_order_logistics?module=95&type=1

入参说明见 references/apis/update-self-collection-order-logistics.md。
"""

from __future__ import annotations

import json
import sys

from _logistics_api_runner import run_logistics_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: update_self_collection_order_logistics.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    run_logistics_api("update_self_collection_order_logistics", params, "update_self_collection_order_logistics.py")


if __name__ == "__main__":
    main()
