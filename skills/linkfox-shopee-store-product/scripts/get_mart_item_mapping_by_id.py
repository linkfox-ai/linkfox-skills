#!/usr/bin/env python3
"""
Shopee Store — get_mart_item_mapping_by_id

官方: https://open.shopee.com/documents/v2/v2.product.get_mart_item_mapping_by_id?module=89&type=1

入参说明见 references/apis/get-mart-item-mapping-by-id.md。
"""

from __future__ import annotations

import json
import sys

from _product_api_runner import run_product_api
from _shopee_product_common import emit_result, lf_inline_flag, load_cli_params


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: get_mart_item_mapping_by_id.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = load_cli_params("get_mart_item_mapping_by_id")
    emit_result(run_product_api("get_mart_item_mapping_by_id", params, "get_mart_item_mapping_by_id.py"), slug="linkfox-shopee-store-product-get_mart_item_mapping_by_id", inline=lf_inline_flag())


if __name__ == "__main__":
    main()
