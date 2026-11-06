#!/usr/bin/env python3
"""
Shopee Store — register_brand

官方: https://open.shopee.com/documents/v2/v2.product.register_brand?module=89&type=1

入参说明见 references/apis/register-brand.md。
"""

from __future__ import annotations

import json
import sys

from _product_api_runner import run_product_api
from _shopee_product_common import emit_result, lf_inline_flag, load_cli_params


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: register_brand.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = load_cli_params("register_brand")
    emit_result(run_product_api("register_brand", params, "register_brand.py"), slug="linkfox-shopee-store-product-register_brand", inline=lf_inline_flag())


if __name__ == "__main__":
    main()
