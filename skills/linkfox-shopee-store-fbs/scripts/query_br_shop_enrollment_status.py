#!/usr/bin/env python3
"""
Shopee Store — query_br_shop_enrollment_status

官方: https://open.shopee.com/documents/v2/v2.fbs.query_br_shop_enrollment_status?module=126&type=1

入参说明见 references/apis/query-br-shop-enrollment-status.md。
"""

from __future__ import annotations

import json
import sys

from _fbs_api_runner import run_fbs_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: query_br_shop_enrollment_status.py '<JSON>' [--inline] [--no-cache]", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    run_fbs_api("query_br_shop_enrollment_status", params, "query_br_shop_enrollment_status.py")


if __name__ == "__main__":
    main()
