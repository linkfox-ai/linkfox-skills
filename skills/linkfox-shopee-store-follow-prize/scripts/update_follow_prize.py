#!/usr/bin/env python3
"""
Shopee Store — update_follow_prize

官方: https://open.shopee.com/documents/v2/v2.follow_prize.update_follow_prize?module=113&type=1

入参说明见 references/apis/update-follow-prize.md。
"""

from __future__ import annotations

import json
import sys

from _follow_prize_api_runner import run_follow_prize_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: update_follow_prize.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    run_follow_prize_api("update_follow_prize", params, "update_follow_prize.py")


if __name__ == "__main__":
    main()
