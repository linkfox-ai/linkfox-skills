#!/usr/bin/env python3
"""
Shopee Store — delete_special_operating_hour

官方: https://open.shopee.com/documents/v2/v2.logistics.delete_special_operating_hour?module=95&type=1

入参说明见 references/apis/delete-special-operating-hour.md。
"""

from __future__ import annotations

import json
import sys

from _logistics_api_runner import run_logistics_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: delete_special_operating_hour.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    run_logistics_api("delete_special_operating_hour", params, "delete_special_operating_hour.py")


if __name__ == "__main__":
    main()
