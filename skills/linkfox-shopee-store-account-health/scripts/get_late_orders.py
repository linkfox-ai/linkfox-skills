#!/usr/bin/env python3
"""
Shopee Store — get_late_orders (v2.account_health.get_late_orders)
官方: https://open.shopee.com/documents/v2/v2.account_health.get_late_orders?module=103&type=1
"""

from __future__ import annotations
from _shopee_account_health_common import emit_result, lf_inline_flag

import json
import sys

from _account_health_api_runner import run_account_health_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: get_late_orders.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    inline = lf_inline_flag()
    emit_result(run_account_health_api("get_late_orders", params, "get_late_orders.py"), inline)


if __name__ == "__main__":
    main()
