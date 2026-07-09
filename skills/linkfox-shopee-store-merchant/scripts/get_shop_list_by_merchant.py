#!/usr/bin/env python3
"""
Shopee Store — get_shop_list_by_merchant (v2.merchant.get_shop_list_by_merchant)
官方: https://open.shopee.com/documents/v2/v2.merchant.get_shop_list_by_merchant?module=93&type=1
"""

from __future__ import annotations

import json
import sys

from _merchant_api_runner import run_merchant_api
from _shopee_merchant_common import emit_result, lf_inline_flag


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: get_shop_list_by_merchant.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    inline = lf_inline_flag()
    emit_result(run_merchant_api("get_shop_list_by_merchant", params, "get_shop_list_by_merchant.py"), inline)


if __name__ == "__main__":
    main()
