#!/usr/bin/env python3
"""
Shopee Store — generic GlobalProduct API caller
================================================

Usage:
  python global_product_api.py '{"api": "get_category", "merchantId": "12345"}'

Official docs: https://open.shopee.com/documents/v2/v2.global_product.<api>?module=90&type=1
"""

from __future__ import annotations

import json
import sys

from _global_product_api_runner import run_global_product_api
from _shopee_global_product_common import emit_result, lf_inline_flag
from _global_product_endpoints import list_api_names


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: global_product_api.py '<JSON with api field>'\nAvailable: {', '.join(list_api_names())}", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    if not params.get("api"):
        print("Missing required field: api", file=sys.stderr)
        sys.exit(1)
    inline = lf_inline_flag()
    emit_result(run_global_product_api(str(params["api"]), params, "global_product_api.py"), inline)


if __name__ == "__main__":
    main()
