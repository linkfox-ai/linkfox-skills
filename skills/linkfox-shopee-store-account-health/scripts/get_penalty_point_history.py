#!/usr/bin/env python3
"""
Shopee Store — get_penalty_point_history (v2.account_health.get_penalty_point_history)
官方: https://open.shopee.com/documents/v2/v2.account_health.get_penalty_point_history?module=103&type=1
"""

from __future__ import annotations
from _shopee_account_health_common import emit_result, lf_inline_flag

import json
import sys

from _account_health_api_runner import run_account_health_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: get_penalty_point_history.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    inline = lf_inline_flag()
    emit_result(run_account_health_api("get_penalty_point_history", params, "get_penalty_point_history.py"), inline)


if __name__ == "__main__":
    main()
