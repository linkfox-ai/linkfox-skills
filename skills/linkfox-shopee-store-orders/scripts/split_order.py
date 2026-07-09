#!/usr/bin/env python3
"""
Shopee Store — split_order (v2.order.split_order)
官方: https://open.shopee.com/documents/v2/v2.order.split_order?module=94&type=1
"""

from __future__ import annotations

import json
import sys

from _order_api_runner import run_order_api
from _shopee_orders_common import emit_result, lf_inline_flag


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: split_order.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    inline = lf_inline_flag()
    emit_result(run_order_api("split_order", params, "split_order.py"), inline)


if __name__ == "__main__":
    main()
