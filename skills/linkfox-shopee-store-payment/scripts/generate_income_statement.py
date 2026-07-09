#!/usr/bin/env python3
"""
Shopee Store — generate_income_statement (v2.payment.generate_income_statement)
官方: https://open.shopee.com/documents/v2/v2.payment.generate_income_statement?module=97&type=1
"""

from __future__ import annotations

import json
import sys

from _payment_api_runner import run_payment_api
from _shopee_payment_common import emit_result, lf_inline_flag


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: generate_income_statement.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    inline = lf_inline_flag()
    emit_result(run_payment_api("generate_income_statement", params, "generate_income_statement.py"), inline)


if __name__ == "__main__":
    main()
