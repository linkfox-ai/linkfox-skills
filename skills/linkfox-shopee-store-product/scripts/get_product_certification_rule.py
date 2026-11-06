#!/usr/bin/env python3
"""
Shopee Store — get_product_certification_rule

官方: https://open.shopee.com/documents/v2/v2.product.get_product_certification_rule?module=89&type=1

入参说明见 references/apis/get-product-certification-rule.md。
"""

from __future__ import annotations

import json
import sys

from _product_api_runner import run_product_api
from _shopee_product_common import emit_result, lf_inline_flag, load_cli_params


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: get_product_certification_rule.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = load_cli_params("get_product_certification_rule")
    emit_result(run_product_api("get_product_certification_rule", params, "get_product_certification_rule.py"), slug="linkfox-shopee-store-product-get_product_certification_rule", inline=lf_inline_flag())


if __name__ == "__main__":
    main()
