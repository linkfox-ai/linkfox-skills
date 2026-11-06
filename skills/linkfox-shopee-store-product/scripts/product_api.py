#!/usr/bin/env python3
"""
Shopee Store — generic Product API caller
=========================================

Usage:
  python product_api.py '{"api": "get_category", "shopId": "67890"}'

Official docs: https://open.shopee.com/documents/v2/v2.product.<api>?module=89&type=1
"""

from __future__ import annotations

import json
import sys

from _product_api_runner import run_product_api
from _product_endpoints import list_api_names
from _shopee_product_common import emit_result, lf_inline_flag, load_cli_params


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: product_api.py '<JSON with api field>'\nAvailable: {', '.join(list_api_names())}", file=sys.stderr)
        sys.exit(1)
    params = load_cli_params()
    if not params.get("api"):
        print("Missing required field: api", file=sys.stderr)
        sys.exit(1)
    inline = lf_inline_flag()
    emit_result(run_product_api(str(params["api"]), params, "product_api.py"), slug="linkfox-shopee-store-product-" + str(params["api"]), inline=inline)


if __name__ == "__main__":
    main()
