#!/usr/bin/env python3
"""
Shopee 店铺秒杀通用入口
===================================================

用法:
  python shop_flash_sale_api.py '{"api": "get_shop_flash_sale_list", "shopId": "67890"}'

官方文档: https://open.shopee.com/documents/v2/v2.shop_flash_sale.<api>?module=123&type=1
"""

from __future__ import annotations

import json
import sys

from _shop_flash_sale_api_runner import lf_inline_flag, run_shop_flash_sale_api
from _shop_flash_sale_endpoints import list_api_names


def main() -> None:
    if len(sys.argv) < 2:
        print(f"用法: shop_flash_sale_api.py '<包含 api 字段的 JSON>'\n可用操作: {', '.join(list_api_names())}", file=sys.stderr)
        sys.exit(1)
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as exc:
        print(f"JSON 参数格式错误: {exc}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(params, dict):
        print("JSON 参数必须为对象", file=sys.stderr)
        sys.exit(1)
    if not params.get("api"):
        print("缺少必填字段: api", file=sys.stderr)
        sys.exit(1)
    inline = lf_inline_flag()
    run_shop_flash_sale_api(str(params["api"]), params, "shop_flash_sale_api.py", display=True, inline=inline)


if __name__ == "__main__":
    main()
