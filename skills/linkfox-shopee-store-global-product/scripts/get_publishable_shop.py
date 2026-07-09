#!/usr/bin/env python3
"""
Shopee Store — get_publishable_shop (v2.global_product.get_publishable_shop)
官方: https://open.shopee.com/documents/v2/v2.global_product.get_publishable_shop?module=90&type=1
"""

from __future__ import annotations

import json
import sys

from _global_product_api_runner import run_global_product_api
from _shopee_global_product_common import emit_result, lf_inline_flag


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: get_publishable_shop.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    inline = lf_inline_flag()
    emit_result(run_global_product_api("get_publishable_shop", params, "get_publishable_shop.py"), inline)


if __name__ == "__main__":
    main()
