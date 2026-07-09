#!/usr/bin/env python3
"""
Shopee Store — get_income_detail (v2.payment.get_income_detail)
官方: https://open.shopee.com/documents/v2/v2.payment.get_income_detail?module=97&type=1
"""

from __future__ import annotations

import json
import sys

from _payment_api_runner import run_payment_api
from _shopee_payment_common import emit_result, lf_inline_flag


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: get_income_detail.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    inline = lf_inline_flag()
    emit_result(run_payment_api("get_income_detail", params, "get_income_detail.py"), inline)


if __name__ == "__main__":
    main()
