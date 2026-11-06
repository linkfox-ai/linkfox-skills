#!/usr/bin/env python3
"""
Shopee Store — update_top_picks

官方: https://open.shopee.com/documents/v2/v2.top_picks.update_top_picks?module=100&type=1

入参说明见 references/apis/update-top-picks.md。
"""

from __future__ import annotations

import sys

from _shopee_top_picks_common import load_cli_params
from _top_picks_api_runner import run_top_picks_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: update_top_picks.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = load_cli_params()
    run_top_picks_api("update_top_picks", params, "update_top_picks.py")


if __name__ == "__main__":
    main()
