#!/usr/bin/env python3
"""
Shopee Store — generic Shop API caller
======================================

Usage:
  python shop_api.py '{"api": "get_shop_info", "shopId": "67890"}'

Official docs: https://open.shopee.com/documents/v2/v2.shop.<api>?module=92&type=1
"""

from __future__ import annotations

import json
import sys

from _shop_api_runner import emit_result, lf_inline_flag, run_shop_api
from _shop_endpoints import list_api_names


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: shop_api.py '<JSON with api field>'\nAvailable: {', '.join(list_api_names())}", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    if not params.get("api"):
        print("Missing required field: api", file=sys.stderr)
        sys.exit(1)
    result = run_shop_api(str(params["api"]), params, "shop_api.py")
    inline = lf_inline_flag()
    emit_result(result, inline)


if __name__ == "__main__":
    main()
