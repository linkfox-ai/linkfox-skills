#!/usr/bin/env python3
"""
Shopee Store — init_tier_variation (v2.global_product.init_tier_variation)
官方: https://open.shopee.com/documents/v2/v2.global_product.init_tier_variation?module=90&type=1
"""

from __future__ import annotations

import json
import sys

from _global_product_api_runner import run_global_product_api
from _shopee_global_product_common import emit_result, lf_inline_flag


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: init_tier_variation.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    inline = lf_inline_flag()
    emit_result(run_global_product_api("init_tier_variation", params, "init_tier_variation.py"), inline)


if __name__ == "__main__":
    main()
