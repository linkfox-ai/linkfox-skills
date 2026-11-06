#!/usr/bin/env python3
"""
Shopee Store — generate_and_bind_first_mile_tracking_number

官方: https://open.shopee.com/documents/v2/v2.first_mile.generate_and_bind_first_mile_tracking_number?module=96&type=1

入参说明见 references/apis/generate-and-bind-first-mile-tracking-number.md。
"""

from __future__ import annotations

import json
import sys

from _first_mile_api_runner import run_first_mile_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: generate_and_bind_first_mile_tracking_number.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    run_first_mile_api("generate_and_bind_first_mile_tracking_number", params, "generate_and_bind_first_mile_tracking_number.py")


if __name__ == "__main__":
    main()
