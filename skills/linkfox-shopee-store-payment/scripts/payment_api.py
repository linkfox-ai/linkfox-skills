#!/usr/bin/env python3
"""
Shopee Store — generic Payment API caller
==========================================

Usage:
  python payment_api.py '{"api": "get_escrow_detail", "shopId": "67890", "order_sn": "240101ABC"}'

Official docs: https://open.shopee.com/documents/v2/v2.payment.<api>?module=97&type=1
"""

from __future__ import annotations

import json
import sys

from _payment_api_runner import run_payment_api
from _payment_endpoints import list_api_names
from _shopee_payment_common import emit_result, lf_inline_flag


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: payment_api.py '<JSON with api field>'\nAvailable: {', '.join(list_api_names())}", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    if not params.get("api"):
        print("Missing required field: api", file=sys.stderr)
        sys.exit(1)
    inline = lf_inline_flag()
    emit_result(run_payment_api(str(params["api"]), params, "payment_api.py"), inline)


if __name__ == "__main__":
    main()
