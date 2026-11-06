#!/usr/bin/env python3
"""
Shopee Store — get_recommend_attribute

官方: https://open.shopee.com/documents/v2/v2.product.get_recommend_attribute?module=89&type=1

入参说明见 references/apis/get-recommend-attribute.md。
"""

from __future__ import annotations

import json
import sys

from _product_api_runner import run_product_api
from _shopee_product_common import emit_result, lf_inline_flag, load_cli_params


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: get_recommend_attribute.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = load_cli_params("get_recommend_attribute")
    emit_result(run_product_api("get_recommend_attribute", params, "get_recommend_attribute.py"), slug="linkfox-shopee-store-product-get_recommend_attribute", inline=lf_inline_flag())


if __name__ == "__main__":
    main()
