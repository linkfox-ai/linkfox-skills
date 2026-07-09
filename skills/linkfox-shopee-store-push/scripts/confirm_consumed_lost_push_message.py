#!/usr/bin/env python3
"""
Shopee Store — confirm_consumed_lost_push_message (v2.push.confirm_consumed_lost_push_message)
官方: https://open.shopee.com/documents/v2/v2.push.confirm_consumed_lost_push_message?module=105&type=1
"""

from __future__ import annotations

import json
import sys

from _push_api_runner import run_push_api
from _shopee_push_common import emit_result, lf_inline_flag


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: confirm_consumed_lost_push_message.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    inline = lf_inline_flag()
    emit_result(run_push_api("confirm_consumed_lost_push_message", params, "confirm_consumed_lost_push_message.py"), inline)


if __name__ == "__main__":
    main()
