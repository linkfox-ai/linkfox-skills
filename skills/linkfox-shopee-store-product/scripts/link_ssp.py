#!/usr/bin/env python3
"""
Shopee Store — link_ssp

官方: https://open.shopee.com/documents/v2/v2.product.link_ssp?module=89&type=1

入参说明见 references/apis/link-ssp.md。
"""

from __future__ import annotations

import json
import sys

from _product_api_runner import run_product_api
from _shopee_product_common import emit_result, lf_inline_flag, load_cli_params


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: link_ssp.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = load_cli_params("link_ssp")
    emit_result(run_product_api("link_ssp", params, "link_ssp.py"), slug="linkfox-shopee-store-product-link_ssp", inline=lf_inline_flag())


if __name__ == "__main__":
    main()
