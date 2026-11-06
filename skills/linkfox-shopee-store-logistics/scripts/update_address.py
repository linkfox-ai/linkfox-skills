#!/usr/bin/env python3
"""
Shopee Store — update_address

官方: https://open.shopee.com/documents/v2/v2.logistics.update_address?module=95&type=1

入参说明见 references/apis/update-address.md。
"""

from __future__ import annotations

import json
import sys

from _logistics_api_runner import run_logistics_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: update_address.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    run_logistics_api("update_address", params, "update_address.py")


if __name__ == "__main__":
    main()
