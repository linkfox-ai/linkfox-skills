#!/usr/bin/env python3
"""
Shopee Store — generate_kit_image (v2.product.generate_kit_image)
官方: https://open.shopee.com/documents/v2/v2.product.generate_kit_image?module=89&type=1
"""

from __future__ import annotations

import json
import sys

from _product_api_runner import run_product_api
from _shopee_product_common import emit_result, lf_inline_flag


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: generate_kit_image.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    inline = lf_inline_flag()
    emit_result(run_product_api("generate_kit_image", params, "generate_kit_image.py"), inline)


if __name__ == "__main__":
    main()
