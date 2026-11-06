#!/usr/bin/env python3
"""
Shopee Store — get_main_item_list

官方: https://open.shopee.com/documents/v2/v2.product.get_main_item_list?module=89&type=1

入参说明见 references/apis/get-main-item-list.md。
"""

from __future__ import annotations

import json
import sys

from _product_api_runner import run_product_api
from _shopee_product_common import emit_result, lf_inline_flag, load_cli_params


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: get_main_item_list.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = load_cli_params("get_main_item_list")
    emit_result(run_product_api("get_main_item_list", params, "get_main_item_list.py"), slug="linkfox-shopee-store-product-get_main_item_list", inline=lf_inline_flag())


if __name__ == "__main__":
    main()
