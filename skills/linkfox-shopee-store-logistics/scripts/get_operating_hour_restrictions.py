#!/usr/bin/env python3
"""
Shopee Store — get_operating_hour_restrictions (v2.logistics.get_operating_hour_restrictions)
官方: https://open.shopee.com/documents/v2/v2.logistics.get_operating_hour_restrictions?module=95&type=1
"""

from __future__ import annotations

import json
import sys

from _logistics_api_runner import run_logistics_api
from _shopee_logistics_common import emit_result, lf_inline_flag


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: get_operating_hour_restrictions.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    inline = lf_inline_flag()
    emit_result(run_logistics_api("get_operating_hour_restrictions", params, "get_operating_hour_restrictions.py"), inline)


if __name__ == "__main__":
    main()
