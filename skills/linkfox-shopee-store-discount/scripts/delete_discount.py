#!/usr/bin/env python3
"""
Shopee Store — delete_discount (v2.discount.delete_discount)
官方: https://open.shopee.com/documents/v2/v2.discount.delete_discount?module=99&type=1
"""

from __future__ import annotations
from _shopee_discount_common import emit_result, lf_inline_flag

import json
import sys

from _discount_api_runner import run_discount_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: delete_discount.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    inline = lf_inline_flag()
    emit_result(run_discount_api("delete_discount", params, "delete_discount.py"), inline)


if __name__ == "__main__":
    main()
