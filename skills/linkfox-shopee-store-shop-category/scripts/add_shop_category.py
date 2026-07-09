#!/usr/bin/env python3
"""
Shopee Store — add_shop_category (v2.shop_category.add_shop_category)
官方: https://open.shopee.com/documents/v2/v2.shop_category.add_shop_category?module=101&type=1
"""

from __future__ import annotations

import json
import sys

from _shop_category_api_runner import emit_result, lf_inline_flag, run_shop_category_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: add_shop_category.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    inline = lf_inline_flag()
    emit_result(run_shop_category_api("add_shop_category", params, "add_shop_category.py"), inline)


if __name__ == "__main__":
    main()
