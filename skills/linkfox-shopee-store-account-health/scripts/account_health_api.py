#!/usr/bin/env python3
"""
Shopee Store — generic Account Health API caller
================================================

Usage:
  python account_health_api.py '{"api": "get_shop_performance", "shopId": "67890"}'

Official docs: https://open.shopee.com/documents/v2/v2.account_health.<api>?module=103&type=1
"""

from __future__ import annotations
from _shopee_account_health_common import emit_result, lf_inline_flag

import json
import sys

from _account_health_api_runner import run_account_health_api
from _account_health_endpoints import list_api_names


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: account_health_api.py '<JSON with api field>'\nAvailable: {', '.join(list_api_names())}", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    if not params.get("api"):
        print("Missing required field: api", file=sys.stderr)
        sys.exit(1)
    inline = lf_inline_flag()
    emit_result(run_account_health_api(str(params["api"]), params, "account_health_api.py"), inline)


if __name__ == "__main__":
    main()
