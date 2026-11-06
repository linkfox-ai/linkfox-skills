#!/usr/bin/env python3
"""
Temu EU order API generic proxy (site=eu, semi-managed, order-shipping token by default).

Usage:
  python temu_eu_proxy.py '{
    "accessToken": "TEMU_US_TOKEN",
    "type": "bg.order.list.v2.get",
    "params": {"request": {"pageNumber": 1, "pageSize": 20, "parentOrderStatus": 2}}
  }'
"""

import json
import sys

from _temu_eu_common import DEFAULT_SITE, eu_proxy_call
from _temu_common import load_json_arg, require_text
def main():
    if len(sys.argv) < 2:
        print("Usage: temu_eu_proxy.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = load_json_arg(sys.argv)
    params.setdefault("site", DEFAULT_SITE)
    api_type = require_text(params, "type")
    eu_proxy_call(params, api_type, display=True)

if __name__ == "__main__":
    main()
