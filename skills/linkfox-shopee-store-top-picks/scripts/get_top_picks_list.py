#!/usr/bin/env python3
"""
Shopee Store — get_top_picks_list

官方: https://open.shopee.com/documents/v2/v2.top_picks.get_top_picks_list?module=100&type=1

入参说明见 references/apis/get-top-picks-list.md。
"""

from __future__ import annotations

import sys

from _shopee_top_picks_common import load_cli_params
from _top_picks_api_runner import run_top_picks_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: get_top_picks_list.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = load_cli_params()
    run_top_picks_api("get_top_picks_list", params, "get_top_picks_list.py")


if __name__ == "__main__":
    main()
