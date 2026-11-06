#!/usr/bin/env python3
"""
Shopee Store — get_kit_item_limit

官方: https://open.shopee.com/documents/v2/v2.product.get_kit_item_limit?module=89&type=1

入参说明见 references/apis/get-kit-item-limit.md。
"""

from __future__ import annotations

import json
import sys

from _product_api_runner import run_product_api
from _shopee_product_common import emit_result, lf_inline_flag, load_cli_params


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: get_kit_item_limit.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = load_cli_params("get_kit_item_limit")
    emit_result(run_product_api("get_kit_item_limit", params, "get_kit_item_limit.py"), slug="linkfox-shopee-store-product-get_kit_item_limit", inline=lf_inline_flag())


if __name__ == "__main__":
    main()
