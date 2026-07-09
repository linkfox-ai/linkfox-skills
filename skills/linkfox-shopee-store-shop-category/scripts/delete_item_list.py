#!/usr/bin/env python3
"""
Shopee Store — delete_item_list (v2.shop_category.delete_item_list)
官方: https://open.shopee.com/documents/v2/v2.shop_category.delete_item_list?module=101&type=1
"""

from __future__ import annotations

import json
import sys

from _shop_category_api_runner import emit_result, lf_inline_flag, run_shop_category_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: delete_item_list.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    inline = lf_inline_flag()
    emit_result(run_shop_category_api("delete_item_list", params, "delete_item_list.py"), inline)


if __name__ == "__main__":
    main()
