#!/usr/bin/env python3
"""
Shopee Store — end_follow_prize (v2.follow_prize.end_follow_prize)
官方: https://open.shopee.com/documents/v2/v2.follow_prize.end_follow_prize?module=113&type=1
"""

from __future__ import annotations

import json
import sys

from _follow_prize_api_runner import run_follow_prize_api
from _shopee_follow_prize_common import emit_result, lf_inline_flag


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: end_follow_prize.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    inline = lf_inline_flag()
    emit_result(run_follow_prize_api("end_follow_prize", params, "end_follow_prize.py"), inline)


if __name__ == "__main__":
    main()
