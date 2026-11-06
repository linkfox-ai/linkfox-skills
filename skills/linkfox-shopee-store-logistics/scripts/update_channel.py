#!/usr/bin/env python3
"""
Shopee Store — update_channel

官方: https://open.shopee.com/documents/v2/v2.logistics.update_channel?module=95&type=1

入参说明见 references/apis/update-channel.md。
"""

from __future__ import annotations

import json
import sys

from _logistics_api_runner import run_logistics_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: update_channel.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    run_logistics_api("update_channel", params, "update_channel.py")


if __name__ == "__main__":
    main()
