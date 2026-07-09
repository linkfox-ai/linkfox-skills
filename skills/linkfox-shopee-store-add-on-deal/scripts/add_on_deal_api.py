#!/usr/bin/env python3
"""
Shopee Store — generic Add-On Deal API caller
===============================================

Usage:
  python add_on_deal_api.py '{"api": "get_add_on_deal_list", "shopId": "67890"}'

Official docs: https://open.shopee.com/documents/v2/v2.add_on_deal.<api>?module=111&type=1
"""

from __future__ import annotations
from _shopee_add_on_deal_common import emit_result, lf_inline_flag

import json
import sys

from _add_on_deal_api_runner import run_add_on_deal_api
from _add_on_deal_endpoints import list_api_names


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: add_on_deal_api.py '<JSON with api field>'\nAvailable: {', '.join(list_api_names())}", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    if not params.get("api"):
        print("Missing required field: api", file=sys.stderr)
        sys.exit(1)
    inline = lf_inline_flag()
    emit_result(run_add_on_deal_api(str(params["api"]), params, "add_on_deal_api.py"), inline)


if __name__ == "__main__":
    main()
