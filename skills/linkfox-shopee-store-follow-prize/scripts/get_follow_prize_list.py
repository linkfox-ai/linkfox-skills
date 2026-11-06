#!/usr/bin/env python3
"""
Shopee Store — get_follow_prize_list

官方: https://open.shopee.com/documents/v2/v2.follow_prize.get_follow_prize_list?module=113&type=1

入参说明见 references/apis/get-follow-prize-list.md。
"""

from __future__ import annotations

import json
import sys

from _follow_prize_api_runner import run_follow_prize_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: get_follow_prize_list.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    run_follow_prize_api("get_follow_prize_list", params, "get_follow_prize_list.py")


if __name__ == "__main__":
    main()
