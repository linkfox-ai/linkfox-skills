#!/usr/bin/env python3
"""
Shopee Store — generic Top Picks API caller
============================================

Usage:
  python top_picks_api.py '{"api": "get_top_picks_list", "shopId": "67890"}'

Official docs: https://open.shopee.com/documents/v2/v2.top_picks.<api>?module=100&type=1
"""

from __future__ import annotations

import sys

from _shopee_top_picks_common import load_cli_params
from _top_picks_api_runner import run_top_picks_api
from _top_picks_endpoints import list_api_names


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: top_picks_api.py '<JSON with api field>'\nAvailable: {', '.join(list_api_names())}", file=sys.stderr)
        sys.exit(1)
    params = load_cli_params()
    if not params.get("api"):
        print("Missing required field: api", file=sys.stderr)
        sys.exit(1)
    run_top_picks_api(str(params["api"]), params, "top_picks_api.py")


if __name__ == "__main__":
    main()
