#!/usr/bin/env python3
"""
Shopee Store — update_tracking_status

官方: https://open.shopee.com/documents/v2/v2.logistics.update_tracking_status?module=95&type=1

入参说明见 references/apis/update-tracking-status.md。
"""

from __future__ import annotations

import json
import sys

from _logistics_api_runner import run_logistics_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: update_tracking_status.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    run_logistics_api("update_tracking_status", params, "update_tracking_status.py")


if __name__ == "__main__":
    main()
