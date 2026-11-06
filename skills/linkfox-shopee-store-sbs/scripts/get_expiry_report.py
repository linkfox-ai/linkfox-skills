#!/usr/bin/env python3
"""
Shopee Store — get_expiry_report

官方: https://open.shopee.com/documents/v2/v2.sbs.get_expiry_report?module=124&type=1

入参说明见 references/apis/get-expiry-report.md。
"""

from __future__ import annotations

import json
import sys

from _sbs_api_runner import run_sbs_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: get_expiry_report.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    run_sbs_api("get_expiry_report", params, "get_expiry_report.py")


if __name__ == "__main__":
    main()
