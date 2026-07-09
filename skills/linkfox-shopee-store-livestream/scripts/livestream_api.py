#!/usr/bin/env python3
"""
Shopee Store — generic Livestream API caller
=============================================

Usage:
  python livestream_api.py '{"api": "get_session_detail", "shopId": "67890"}'

Official docs: https://open.shopee.com/documents/v2/v2.livestream.<api>?module=125&type=1
"""

from __future__ import annotations

import json
import sys

from _livestream_api_runner import run_livestream_api
from _livestream_endpoints import list_api_names
from _shopee_livestream_common import emit_result, lf_inline_flag


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: livestream_api.py '<JSON with api field>'\nAvailable: {', '.join(list_api_names())}", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    if not params.get("api"):
        print("Missing required field: api", file=sys.stderr)
        sys.exit(1)
    inline = lf_inline_flag()
    emit_result(run_livestream_api(str(params["api"]), params, "livestream_api.py"), inline)


if __name__ == "__main__":
    main()
