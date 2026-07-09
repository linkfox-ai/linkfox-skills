#!/usr/bin/env python3
"""
Temu EU tax API generic proxy (site=eu, semi-managed by default).

Usage:
  python temu_eu_proxy.py '{
    "accessToken": "TEMU_EU_TOKEN",
    "type": "<temu.tax.type.from.partner.doc>",
    "request": { }
  }'
"""

import json
import sys

from _temu_common import load_json_arg, parse_nested_body, require_text, emit_result, lf_inline_flag
from _temu_eu_common import DEFAULT_SITE, eu_proxy_call

def main():
    if len(sys.argv) < 2:
        print("Usage: temu_eu_proxy.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = load_json_arg(sys.argv)
    params.setdefault("site", DEFAULT_SITE)
    api_type = require_text(params, "type")
    result = parse_nested_body(eu_proxy_call(params, api_type))
    inline = lf_inline_flag()
    emit_result(result, inline)

if __name__ == "__main__":
    main()
