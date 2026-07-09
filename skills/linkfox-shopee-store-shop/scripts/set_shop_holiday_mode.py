#!/usr/bin/env python3
"""
Shopee Store — set_shop_holiday_mode (v2.shop.set_shop_holiday_mode)
官方: https://open.shopee.com/documents/v2/v2.shop.set_shop_holiday_mode?module=92&type=1
"""

from __future__ import annotations

import json
import sys

from _shop_api_runner import emit_result, lf_inline_flag, run_shop_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: set_shop_holiday_mode.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    result = run_shop_api("set_shop_holiday_mode", params, "set_shop_holiday_mode.py")
    inline = lf_inline_flag()
    emit_result(result, inline)


if __name__ == "__main__":
    main()
