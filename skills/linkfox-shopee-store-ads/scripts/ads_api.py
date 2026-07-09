#!/usr/bin/env python3
"""
Shopee Store — generic Ads API caller
======================================

Usage:
  python ads_api.py '{"api": "get_total_balance", "shopId": "67890"}'

Official docs: https://open.shopee.com/documents/v2/v2.ads.<api>?module=117&type=1
"""

from __future__ import annotations
from _shopee_ads_common import emit_result, lf_inline_flag

import json
import sys

from _ads_api_runner import run_ads_api
from _ads_endpoints import list_api_names


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: ads_api.py '<JSON with api field>'\nAvailable: {', '.join(list_api_names())}", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    if not params.get("api"):
        print("Missing required field: api", file=sys.stderr)
        sys.exit(1)
    inline = lf_inline_flag()
    emit_result(run_ads_api(str(params["api"]), params, "ads_api.py"), inline)


if __name__ == "__main__":
    main()
