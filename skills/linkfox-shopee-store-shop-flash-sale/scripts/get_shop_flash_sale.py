#!/usr/bin/env python3
"""
Shopee 店铺秒杀 — get_shop_flash_sale

官方: https://open.shopee.com/documents/v2/v2.shop_flash_sale.get_shop_flash_sale?module=123&type=1

入参说明见 references/apis/get-shop-flash-sale.md。
"""

from __future__ import annotations

import json
import sys

from _shop_flash_sale_api_runner import lf_inline_flag, run_shop_flash_sale_api


def main() -> None:
    if len(sys.argv) < 2:
        print("用法: get_shop_flash_sale.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as exc:
        print(f"JSON 参数格式错误: {exc}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(params, dict):
        print("JSON 参数必须为对象", file=sys.stderr)
        sys.exit(1)
    inline = lf_inline_flag()
    run_shop_flash_sale_api("get_shop_flash_sale", params, "get_shop_flash_sale.py", display=True, inline=inline)


if __name__ == "__main__":
    main()
