#!/usr/bin/env python3
"""
Shopee Store — delete_item (v2.product.delete_item)
官方: https://open.shopee.com/documents/v2/v2.product.delete_item?module=89&type=1
"""

from __future__ import annotations

import json
import sys

from _product_api_runner import run_product_api
from _shopee_product_common import emit_result, lf_inline_flag


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: delete_item.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    inline = lf_inline_flag()
    emit_result(run_product_api("delete_item", params, "delete_item.py"), inline)


if __name__ == "__main__":
    main()
