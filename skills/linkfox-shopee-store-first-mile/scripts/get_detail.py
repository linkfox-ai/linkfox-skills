#!/usr/bin/env python3
"""
Shopee Store — get_detail

官方: https://open.shopee.com/documents/v2/v2.first_mile.get_detail?module=96&type=1

入参说明见 references/apis/get-detail.md。
"""

from __future__ import annotations

import json
import sys

from _first_mile_api_runner import run_first_mile_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: get_detail.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    run_first_mile_api("get_detail", params, "get_detail.py")


if __name__ == "__main__":
    main()
