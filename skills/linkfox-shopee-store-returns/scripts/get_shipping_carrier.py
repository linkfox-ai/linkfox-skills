#!/usr/bin/env python3
"""
Shopee Store — get_shipping_carrier (v2.returns.get_shipping_carrier)
官方: https://open.shopee.com/documents/v2/v2.returns.get_shipping_carrier?module=102&type=1
"""

from __future__ import annotations

import json
import sys

from _returns_api_runner import run_returns_api
from _shopee_returns_common import emit_result, lf_inline_flag


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: get_shipping_carrier.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    inline = lf_inline_flag()
    emit_result(run_returns_api("get_shipping_carrier", params, "get_shipping_carrier.py"), inline)


if __name__ == "__main__":
    main()
