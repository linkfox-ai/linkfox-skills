#!/usr/bin/env python3
"""
Shopee Store — set_address_config (v2.logistics.set_address_config)
官方: https://open.shopee.com/documents/v2/v2.logistics.set_address_config?module=95&type=1
"""

from __future__ import annotations

import json
import sys

from _logistics_api_runner import run_logistics_api
from _shopee_logistics_common import emit_result, lf_inline_flag


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: set_address_config.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    inline = lf_inline_flag()
    emit_result(run_logistics_api("set_address_config", params, "set_address_config.py"), inline)


if __name__ == "__main__":
    main()
