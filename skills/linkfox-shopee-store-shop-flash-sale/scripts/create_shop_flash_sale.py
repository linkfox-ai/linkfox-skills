#!/usr/bin/env python3
"""
Shopee Store — create_shop_flash_sale (v2.shop_flash_sale.create_shop_flash_sale)
官方: https://open.shopee.com/documents/v2/v2.shop_flash_sale.create_shop_flash_sale?module=123&type=1
"""

from __future__ import annotations

import json
import sys

from _shop_flash_sale_api_runner import emit_result, lf_inline_flag, run_shop_flash_sale_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: create_shop_flash_sale.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    inline = lf_inline_flag()
    emit_result(run_shop_flash_sale_api("create_shop_flash_sale", params, "create_shop_flash_sale.py"), inline)


if __name__ == "__main__":
    main()
