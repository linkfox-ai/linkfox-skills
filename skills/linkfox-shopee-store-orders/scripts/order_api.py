#!/usr/bin/env python3
"""
Shopee Store — generic Order API caller
=======================================

Usage:
  python order_api.py '{"api": "cancel_order", "shopId": "67890", "order_sn": "...", "cancel_reason": "OUT_OF_STOCK"}'

`api` must be one of the Order module endpoints. Official docs pattern:
  https://open.shopee.com/documents/v2/v2.order.<api>?module=94&type=1

See `references/api.md` and `_order_endpoints.official_doc_url()`.
"""

from __future__ import annotations

import json
import sys

from _order_api_runner import run_order_api
from _order_endpoints import list_api_names
from _shopee_orders_common import emit_result, lf_inline_flag


def main() -> None:
    if len(sys.argv) < 2:
        names = ", ".join(list_api_names())
        print(f"Usage: order_api.py '<JSON with api field>'\nAvailable api: {names}", file=sys.stderr)
        sys.exit(1)
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    api_name = params.get("api")
    if not api_name:
        print("Missing required field: api", file=sys.stderr)
        sys.exit(1)
    result = run_order_api(str(api_name), params, "order_api.py")
    inline = lf_inline_flag()
    emit_result(result, inline)


if __name__ == "__main__":
    main()
