#!/usr/bin/env python3
"""
Shopee Store — generic Public API caller
=========================================

Usage:
  python public_api.py '{"api": "get_shops_by_partner"}'

Official docs: https://open.shopee.com/documents/v2/v2.public.<api>?module=104&type=1
"""

from __future__ import annotations

import json
import sys

from _public_api_runner import run_public_api
from _public_endpoints import list_api_names
from _shopee_public_common import emit_result, lf_inline_flag


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: public_api.py '<JSON with api field>'\nAvailable: {', '.join(list_api_names())}", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    if not params.get("api"):
        print("Missing required field: api", file=sys.stderr)
        sys.exit(1)
    inline = lf_inline_flag()
    emit_result(run_public_api(str(params["api"]), params, "public_api.py"), inline)


if __name__ == "__main__":
    main()
