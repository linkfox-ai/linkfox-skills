#!/usr/bin/env python3
"""
Shopee Store — generic Follow Prize API caller
===============================================

Usage:
  python follow_prize_api.py '{"api": "get_follow_prize_list", "shopId": "67890"}'

Official docs: https://open.shopee.com/documents/v2/v2.follow_prize.<api>?module=113&type=1
"""

from __future__ import annotations

import json
import sys

from _follow_prize_api_runner import run_follow_prize_api
from _follow_prize_endpoints import list_api_names
from _shopee_follow_prize_common import emit_result, lf_inline_flag


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: follow_prize_api.py '<JSON with api field>'\nAvailable: {', '.join(list_api_names())}", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    if not params.get("api"):
        print("Missing required field: api", file=sys.stderr)
        sys.exit(1)
    inline = lf_inline_flag()
    emit_result(run_follow_prize_api(str(params["api"]), params, "follow_prize_api.py"), inline)


if __name__ == "__main__":
    main()
