#!/usr/bin/env python3
"""
Temu US seller cancel-order API generic proxy (site=us, semi-managed, order-shipping token by default).

Usage:
  python temu_us_proxy.py '{
    "accessToken": "TEMU_US_TOKEN",
    "tokenPurpose": "order-shipping",
    "type": "<TEMU_API_TYPE>",
    "params": {"request": {}}
  }'
"""

import json
import sys

from _temu_us_common import DEFAULT_SITE, us_proxy_call
from _temu_common import load_json_arg, parse_nested_body, require_text
from _temu_us_common import emit_result, lf_inline_flag

def main():
    if len(sys.argv) < 2:
        print("Usage: temu_us_proxy.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = load_json_arg(sys.argv)
    params.setdefault("site", DEFAULT_SITE)
    api_type = require_text(params, "type")
    result = parse_nested_body(us_proxy_call(params, api_type))
    emit_result(result, inline=lf_inline_flag())

if __name__ == "__main__":
    main()
