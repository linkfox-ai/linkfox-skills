#!/usr/bin/env python3
"""
Shopee Store — generic Order API caller
=======================================

Usage:
  python order_api.py '{"api": "cancel_order", "shopId": "67890", "order_sn": "...", "cancel_reason": "OUT_OF_STOCK"}'

`api` must be one of the Order module endpoints. Official docs pattern:
  https://open.shopee.com/documents/v2/v2.order.<api>?module=94&type=1

See `references/api.md` and the per-operation references.
"""

from __future__ import annotations

import json
import sys

from _order_api_runner import run_order_api
from _order_endpoints import list_api_names


def main() -> None:
    if len(sys.argv) < 2:
        names = ", ".join(list_api_names())
        print(f"Usage: order_api.py '<JSON with api field>'\nAvailable api: {names}", file=sys.stderr)
        sys.exit(1)
    if sys.argv[1] in ("-h", "--help"):
        print("用法：order_api.py '<含 api 的 JSON 参数>' [--inline] [--no-cache]")
        print("支持操作：" + ", ".join(list_api_names()))
        return
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(params, dict):
        print("JSON parameters must be an object", file=sys.stderr)
        raise SystemExit(1)
    api_name = params.get("api")
    if not api_name:
        print("Missing required field: api", file=sys.stderr)
        sys.exit(1)
    run_order_api(str(api_name), params, "order_api.py")


if __name__ == "__main__":
    main()
