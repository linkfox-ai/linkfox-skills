#!/usr/bin/env python3
"""
Temu Global price API generic proxy (site=global, semi-managed by default).

Usage:
  python temu_global_proxy.py '{
    "accessToken": "TEMU_US_TOKEN",
    "type": "bg.local.goods.priceorder.query",
    "params": {"request": {"page": 1, "size": 20, "priceOrderType": 1}}
  }'
"""

import json
import sys

from _temu_global_common import DEFAULT_SITE, global_proxy_call
from _temu_common import emit_result, lf_inline_flag, load_json_arg, parse_nested_body, require_text

def main():
    if len(sys.argv) < 2:
        print("Usage: temu_global_proxy.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = load_json_arg(sys.argv)
    params.setdefault("site", DEFAULT_SITE)
    api_type = require_text(params, "type")
    result = parse_nested_body(global_proxy_call(params, api_type))
    emit_result(result, inline=lf_inline_flag())

if __name__ == "__main__":
    main()
