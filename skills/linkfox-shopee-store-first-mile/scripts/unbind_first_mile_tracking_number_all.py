#!/usr/bin/env python3
"""
Shopee Store — unbind_first_mile_tracking_number_all

官方: https://open.shopee.com/documents/v2/v2.first_mile.unbind_first_mile_tracking_number_all?module=96&type=1

入参说明见 references/apis/unbind-first-mile-tracking-number-all.md。
"""

from __future__ import annotations

import json
import sys

from _first_mile_api_runner import run_first_mile_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: unbind_first_mile_tracking_number_all.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    run_first_mile_api("unbind_first_mile_tracking_number_all", params, "unbind_first_mile_tracking_number_all.py")


if __name__ == "__main__":
    main()
