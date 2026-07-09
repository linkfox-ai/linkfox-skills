#!/usr/bin/env python3
"""
Shopee Store — generic Shop Flash Sale API caller
===================================================

Usage:
  python shop_flash_sale_api.py '{"api": "get_shop_flash_sale_list", "shopId": "67890"}'

Official docs: https://open.shopee.com/documents/v2/v2.shop_flash_sale.<api>?module=123&type=1
"""

from __future__ import annotations

import json
import sys

from _shop_flash_sale_api_runner import emit_result, lf_inline_flag, run_shop_flash_sale_api
from _shop_flash_sale_endpoints import list_api_names


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: shop_flash_sale_api.py '<JSON with api field>'\nAvailable: {', '.join(list_api_names())}", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    if not params.get("api"):
        print("Missing required field: api", file=sys.stderr)
        sys.exit(1)
    inline = lf_inline_flag()
    emit_result(run_shop_flash_sale_api(str(params["api"]), params, "shop_flash_sale_api.py"), inline)


if __name__ == "__main__":
    main()
