#!/usr/bin/env python3
"""
Shopee Store — search_attribute_value_list

官方: https://open.shopee.com/documents/v2/v2.product.search_attribute_value_list?module=89&type=1

入参说明见 references/apis/search-attribute-value-list.md。
"""

from __future__ import annotations

import json
import sys

from _product_api_runner import run_product_api
from _shopee_product_common import emit_result, lf_inline_flag, load_cli_params


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: search_attribute_value_list.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = load_cli_params("search_attribute_value_list")
    emit_result(run_product_api("search_attribute_value_list", params, "search_attribute_value_list.py"), slug="linkfox-shopee-store-product-search_attribute_value_list", inline=lf_inline_flag())


if __name__ == "__main__":
    main()
