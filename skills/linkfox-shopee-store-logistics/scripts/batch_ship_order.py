#!/usr/bin/env python3
"""
Shopee Store — batch_ship_order

官方: https://open.shopee.com/documents/v2/v2.logistics.batch_ship_order?module=95&type=1

入参说明见 references/apis/batch-ship-order.md。
"""

from __future__ import annotations

import json
import sys

from _logistics_api_runner import run_logistics_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: batch_ship_order.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    run_logistics_api("batch_ship_order", params, "batch_ship_order.py")


if __name__ == "__main__":
    main()
