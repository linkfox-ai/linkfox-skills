#!/usr/bin/env python3
"""
Shopee Store — search_global_attribute_value_list (v2.global_product.search_global_attribute_value_list)
官方: https://open.shopee.com/documents/v2/v2.global_product.search_global_attribute_value_list?module=90&type=1
"""

from __future__ import annotations

import json
import sys

from _global_product_api_runner import run_global_product_api
from _shopee_global_product_common import emit_result, lf_inline_flag


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: search_global_attribute_value_list.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    inline = lf_inline_flag()
    emit_result(run_global_product_api("search_global_attribute_value_list", params, "search_global_attribute_value_list.py"), inline)


if __name__ == "__main__":
    main()
