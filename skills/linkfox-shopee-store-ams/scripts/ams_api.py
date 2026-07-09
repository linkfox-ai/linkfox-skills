#!/usr/bin/env python3
"""
Shopee Store — generic AMS API caller
======================================

Usage:
  python ams_api.py '{"api": "get_open_campaign_added_product", "shopId": "67890"}'

Official docs: https://open.shopee.com/documents/v2/v2.ams.<api>?module=127&type=1
"""

from __future__ import annotations
from _shopee_ams_common import emit_result, lf_inline_flag

import json
import sys

from _ams_api_runner import run_ams_api
from _ams_endpoints import list_api_names


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: ams_api.py '<JSON with api field>'\nAvailable: {', '.join(list_api_names())}", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    if not params.get("api"):
        print("Missing required field: api", file=sys.stderr)
        sys.exit(1)
    inline = lf_inline_flag()
    emit_result(run_ams_api(str(params["api"]), params, "ams_api.py"), inline)


if __name__ == "__main__":
    main()
