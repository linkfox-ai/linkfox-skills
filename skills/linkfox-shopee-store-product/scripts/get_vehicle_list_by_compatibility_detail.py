#!/usr/bin/env python3
"""
Shopee Store — get_vehicle_list_by_compatibility_detail

官方: https://open.shopee.com/documents/v2/v2.product.get_vehicle_list_by_compatibility_detail?module=89&type=1

入参说明见 references/apis/get-vehicle-list-by-compatibility-detail.md。
"""

from __future__ import annotations

import json
import sys

from _product_api_runner import run_product_api
from _shopee_product_common import emit_result, lf_inline_flag, load_cli_params


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: get_vehicle_list_by_compatibility_detail.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = load_cli_params("get_vehicle_list_by_compatibility_detail")
    emit_result(run_product_api("get_vehicle_list_by_compatibility_detail", params, "get_vehicle_list_by_compatibility_detail.py"), slug="linkfox-shopee-store-product-get_vehicle_list_by_compatibility_detail", inline=lf_inline_flag())


if __name__ == "__main__":
    main()
