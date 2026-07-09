#!/usr/bin/env python3
"""
Shopee Store — generic Push API caller
======================================

Usage:
  python push_api.py '{"api": "get_app_push_config"}'

Official docs: https://open.shopee.com/documents/v2/v2.push.<api>?module=105&type=1
"""

from __future__ import annotations

import json
import sys

from _push_api_runner import run_push_api
from _push_endpoints import list_api_names
from _shopee_push_common import emit_result, lf_inline_flag


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: push_api.py '<JSON with api field>'\nAvailable: {', '.join(list_api_names())}", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    if not params.get("api"):
        print("Missing required field: api", file=sys.stderr)
        sys.exit(1)
    inline = lf_inline_flag()
    emit_result(run_push_api(str(params["api"]), params, "push_api.py"), inline)


if __name__ == "__main__":
    main()
