#!/usr/bin/env python3
"""
Shopee Store — query_br_shop_invoice_error (v2.fbs.query_br_shop_invoice_error)
官方: https://open.shopee.com/documents/v2/v2.fbs.query_br_shop_invoice_error?module=126&type=1
"""

from __future__ import annotations
from _shopee_fbs_common import emit_result, lf_inline_flag

import json
import sys

from _fbs_api_runner import run_fbs_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: query_br_shop_invoice_error.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    inline = lf_inline_flag()
    emit_result(run_fbs_api("query_br_shop_invoice_error", params, "query_br_shop_invoice_error.py"), inline)


if __name__ == "__main__":
    main()
