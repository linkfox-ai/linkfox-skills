#!/usr/bin/env python3
"""
Shopee Store — get_item_promotion

官方: https://open.shopee.com/documents/v2/v2.product.get_item_promotion?module=89&type=1

入参说明见 references/apis/get-item-promotion.md。
"""

from __future__ import annotations

import json
import sys

from _product_api_runner import run_product_api
from _shopee_product_common import emit_result, lf_inline_flag, load_cli_params


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: get_item_promotion.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = load_cli_params("get_item_promotion")
    emit_result(run_product_api("get_item_promotion", params, "get_item_promotion.py"), slug="linkfox-shopee-store-product-get_item_promotion", inline=lf_inline_flag())


if __name__ == "__main__":
    main()
