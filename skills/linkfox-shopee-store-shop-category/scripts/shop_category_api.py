#!/usr/bin/env python3
"""
Shopee Store — generic Shop Category API caller
===============================================

Usage:
  python shop_category_api.py '{"api": "get_shop_category_list", "shopId": "67890"}'

Official docs: https://open.shopee.com/documents/v2/v2.shop_category.<api>?module=101&type=1
"""

from __future__ import annotations

import json
import sys

from _shop_category_api_runner import emit_result, lf_inline_flag, run_shop_category_api
from _shop_category_endpoints import list_api_names


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: shop_category_api.py '<JSON with api field>'\nAvailable: {', '.join(list_api_names())}", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    if not params.get("api"):
        print("Missing required field: api", file=sys.stderr)
        sys.exit(1)
    inline = lf_inline_flag()
    emit_result(run_shop_category_api(str(params["api"]), params, "shop_category_api.py"), inline)


if __name__ == "__main__":
    main()
