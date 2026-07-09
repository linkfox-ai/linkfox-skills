#!/usr/bin/env python3
"""
Shopee Store — delete_global_model (v2.global_product.delete_global_model)
官方: https://open.shopee.com/documents/v2/v2.global_product.delete_global_model?module=90&type=1
"""

from __future__ import annotations

import json
import sys

from _global_product_api_runner import run_global_product_api
from _shopee_global_product_common import emit_result, lf_inline_flag


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: delete_global_model.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    inline = lf_inline_flag()
    emit_result(run_global_product_api("delete_global_model", params, "delete_global_model.py"), inline)


if __name__ == "__main__":
    main()
