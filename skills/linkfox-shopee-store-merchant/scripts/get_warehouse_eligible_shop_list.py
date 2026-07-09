#!/usr/bin/env python3
"""
Shopee Store — get_warehouse_eligible_shop_list (v2.merchant.get_warehouse_eligible_shop_list)
官方: https://open.shopee.com/documents/v2/v2.merchant.get_warehouse_eligible_shop_list?module=93&type=1
"""

from __future__ import annotations

import json
import sys

from _merchant_api_runner import run_merchant_api
from _shopee_merchant_common import emit_result, lf_inline_flag


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: get_warehouse_eligible_shop_list.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    inline = lf_inline_flag()
    emit_result(run_merchant_api("get_warehouse_eligible_shop_list", params, "get_warehouse_eligible_shop_list.py"), inline)


if __name__ == "__main__":
    main()
