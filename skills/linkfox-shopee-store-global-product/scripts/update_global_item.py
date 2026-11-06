#!/usr/bin/env python3
"""
Shopee Store — update_global_item

官方: https://open.shopee.com/documents/v2/v2.global_product.update_global_item?module=90&type=1

入参说明见 references/apis/update-global-item.md。
"""

from __future__ import annotations

import json
import sys

from _global_product_api_runner import run_global_product_api
from _shopee_global_product_common import emit_result, lf_inline_flag


def main() -> None:
    if "--help" in sys.argv[1:] or "-h" in sys.argv[1:]:
        print("用法: update_global_item.py '<JSON>' [--inline] [--no-cache]")
        return
    if len(sys.argv) < 2:
        print("Usage: update_global_item.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    emit_result(run_global_product_api("update_global_item", params, "update_global_item.py"), slug="linkfox-shopee-store-global-product-update_global_item", inline=lf_inline_flag())


if __name__ == "__main__":
    main()
