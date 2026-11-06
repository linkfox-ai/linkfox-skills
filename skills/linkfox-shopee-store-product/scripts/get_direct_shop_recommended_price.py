#!/usr/bin/env python3
"""
Shopee Store — get_direct_shop_recommended_price

官方: https://open.shopee.com/documents/v2/v2.product.get_direct_shop_recommended_price?module=89&type=1

入参说明见 references/apis/get-direct-shop-recommended-price.md。
"""

from __future__ import annotations

import json
import sys

from _product_api_runner import run_product_api
from _shopee_product_common import emit_result, lf_inline_flag, load_cli_params


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: get_direct_shop_recommended_price.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = load_cli_params("get_direct_shop_recommended_price")
    emit_result(run_product_api("get_direct_shop_recommended_price", params, "get_direct_shop_recommended_price.py"), slug="linkfox-shopee-store-product-get_direct_shop_recommended_price", inline=lf_inline_flag())


if __name__ == "__main__":
    main()
