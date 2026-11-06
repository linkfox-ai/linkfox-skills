#!/usr/bin/env python3
"""
Shopee Store — get_category

官方: https://open.shopee.com/documents/v2/v2.global_product.get_category?module=90&type=1

入参说明见 references/apis/get-category.md。
"""

from __future__ import annotations

import json
import sys

from _global_product_api_runner import run_global_product_api
from _shopee_global_product_common import emit_result, lf_inline_flag


def main() -> None:
    if "--help" in sys.argv[1:] or "-h" in sys.argv[1:]:
        print("用法: get_category.py '<JSON>' [--inline] [--no-cache]")
        return
    if len(sys.argv) < 2:
        print("Usage: get_category.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    emit_result(run_global_product_api("get_category", params, "get_category.py"), slug="linkfox-shopee-store-global-product-get_category", inline=lf_inline_flag())


if __name__ == "__main__":
    main()
