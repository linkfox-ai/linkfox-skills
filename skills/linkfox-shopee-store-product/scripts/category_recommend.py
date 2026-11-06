#!/usr/bin/env python3
"""
Shopee Store — category_recommend

官方: https://open.shopee.com/documents/v2/v2.product.category_recommend?module=89&type=1

入参说明见 references/apis/category-recommend.md。
"""

from __future__ import annotations

import json
import sys

from _product_api_runner import run_product_api
from _shopee_product_common import emit_result, lf_inline_flag, load_cli_params


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: category_recommend.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = load_cli_params("category_recommend")
    emit_result(run_product_api("category_recommend", params, "category_recommend.py"), slug="linkfox-shopee-store-product-category_recommend", inline=lf_inline_flag())


if __name__ == "__main__":
    main()
