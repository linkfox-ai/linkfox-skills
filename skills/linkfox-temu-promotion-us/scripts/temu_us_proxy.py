#!/usr/bin/env python3
"""
Temu US Promotion generic proxy (site=us, semi-managed by default).

Usage:
  python temu_us_proxy.py '{
    "accessToken": "TOKEN",
    "tokenPurpose": "product-inventory",
    "type": "<TEMU_API_TYPE>",
    "params": {
      "request": {}
    }
  }'
"""

import json
import sys

from _temu_common import load_json_arg, parse_nested_body, require_text, emit_result, lf_inline_flag
from _temu_us_common import DEFAULT_SITE, us_proxy_call

def main():
    if len(sys.argv) < 2:
        print("Usage: temu_us_proxy.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = load_json_arg(sys.argv)
    params.setdefault("site", DEFAULT_SITE)
    api_type = require_text(params, "type")
    result = parse_nested_body(us_proxy_call(params, api_type))
    inline = lf_inline_flag()
    emit_result(result, inline)

if __name__ == "__main__":
    main()
