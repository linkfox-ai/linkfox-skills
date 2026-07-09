#!/usr/bin/env python3
"""
Shopee Store — generic FBS API caller
======================================

Usage:
  python fbs_api.py '{"api": "query_br_shop_enrollment_status", "shopId": "67890"}'

Official docs: https://open.shopee.com/documents/v2/v2.fbs.<api>?module=126&type=1
"""

from __future__ import annotations
from _shopee_fbs_common import emit_result, lf_inline_flag

import json
import sys

from _fbs_api_runner import run_fbs_api
from _fbs_endpoints import list_api_names


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: fbs_api.py '<JSON with api field>'\nAvailable: {', '.join(list_api_names())}", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    if not params.get("api"):
        print("Missing required field: api", file=sys.stderr)
        sys.exit(1)
    inline = lf_inline_flag()
    emit_result(run_fbs_api(str(params["api"]), params, "fbs_api.py"), inline)


if __name__ == "__main__":
    main()
