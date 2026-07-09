#!/usr/bin/env python3
"""
Shopee Store — generic Merchant API caller
==========================================

Usage:
  python merchant_api.py '{"api": "get_merchant_info", "merchantId": "12345"}'

Official docs: https://open.shopee.com/documents/v2/v2.merchant.<api>?module=93&type=1
"""

from __future__ import annotations

import json
import sys

from _merchant_api_runner import run_merchant_api
from _merchant_endpoints import list_api_names
from _shopee_merchant_common import emit_result, lf_inline_flag


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: merchant_api.py '<JSON with api field>'\nAvailable: {', '.join(list_api_names())}", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    if not params.get("api"):
        print("Missing required field: api", file=sys.stderr)
        sys.exit(1)
    inline = lf_inline_flag()
    emit_result(run_merchant_api(str(params["api"]), params, "merchant_api.py"), inline)


if __name__ == "__main__":
    main()
