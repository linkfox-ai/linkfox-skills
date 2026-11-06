#!/usr/bin/env python3
"""
Shopee Store — generic FirstMile API caller
==============================================

Usage:
  python first_mile_api.py '{"api": "get_unbind_order_list", "shopId": "67890"}'

Official docs: https://open.shopee.com/documents/v2/v2.first_mile.<api>?module=96&type=1
"""

from __future__ import annotations

import json
import sys

from _first_mile_api_runner import run_first_mile_api
from _first_mile_endpoints import list_api_names


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: first_mile_api.py '<JSON with api field>'\nAvailable: {', '.join(list_api_names())}", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    if not params.get("api"):
        print("Missing required field: api", file=sys.stderr)
        sys.exit(1)
    run_first_mile_api(str(params["api"]), params, "first_mile_api.py")


if __name__ == "__main__":
    main()
