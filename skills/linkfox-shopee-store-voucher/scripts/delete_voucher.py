#!/usr/bin/env python3
"""
Shopee Store — delete_voucher (v2.voucher.delete_voucher)
官方: https://open.shopee.com/documents/v2/v2.voucher.delete_voucher?module=112&type=1
"""

from __future__ import annotations

import json
import sys

from _voucher_api_runner import run_voucher_api
from _shopee_voucher_common import emit_result, lf_inline_flag


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: delete_voucher.py '<JSON>' [--inline]", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    inline = lf_inline_flag()
    emit_result(run_voucher_api("delete_voucher", params, "delete_voucher.py"), inline)


if __name__ == "__main__":
    main()
