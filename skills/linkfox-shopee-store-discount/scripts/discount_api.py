#!/usr/bin/env python3
"""
Shopee Store — generic Discount API caller
=============================================

Usage:
  python discount_api.py '{"api": "get_discount_list", "shopId": "67890"}'

Official docs: https://open.shopee.com/documents/v2/v2.discount.<api>?module=99&type=1
"""

from __future__ import annotations
from _shopee_discount_common import emit_result, lf_inline_flag

import json
import sys

from _discount_api_runner import run_discount_api
from _discount_endpoints import list_api_names


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: discount_api.py '<JSON with api field>'\nAvailable: {', '.join(list_api_names())}", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    if not params.get("api"):
        print("Missing required field: api", file=sys.stderr)
        sys.exit(1)
    inline = lf_inline_flag()
    emit_result(run_discount_api(str(params["api"]), params, "discount_api.py"), inline)


if __name__ == "__main__":
    main()
