#!/usr/bin/env python3
"""
Shopee Store — generic Voucher API caller
===========================================

Usage:
  python voucher_api.py '{"api": "get_voucher_list", "shopId": "67890"}'

Official docs: https://open.shopee.com/documents/v2/v2.voucher.<api>?module=112&type=1
"""

from __future__ import annotations

import json
import sys

from _voucher_api_runner import run_voucher_api
from _voucher_endpoints import list_api_names
from _shopee_voucher_common import emit_result, lf_inline_flag


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: voucher_api.py '<JSON with api field>' [--inline]\nAvailable: {', '.join(list_api_names())}", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    if not params.get("api"):
        print("Missing required field: api", file=sys.stderr)
        sys.exit(1)
    inline = lf_inline_flag()
    emit_result(run_voucher_api(str(params["api"]), params, "voucher_api.py"), inline)


if __name__ == "__main__":
    main()
