#!/usr/bin/env python3
"""
Shopee Store — add_item

官方: https://open.shopee.com/documents/v2/v2.product.add_item?module=89&type=1

入参说明见 references/apis/add-item.md。
"""

from __future__ import annotations

import json
import sys

from _product_api_runner import run_product_api
from _shopee_product_common import emit_result, lf_inline_flag, load_cli_params


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: add_item.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = load_cli_params("add_item")
    emit_result(run_product_api("add_item", params, "add_item.py"), slug="linkfox-shopee-store-product-add_item", inline=lf_inline_flag())


if __name__ == "__main__":
    main()
