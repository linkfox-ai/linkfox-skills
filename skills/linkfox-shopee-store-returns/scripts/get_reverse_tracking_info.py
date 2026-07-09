#!/usr/bin/env python3
"""
Shopee Store — get_reverse_tracking_info (v2.returns.get_reverse_tracking_info)
官方: https://open.shopee.com/documents/v2/v2.returns.get_reverse_tracking_info?module=102&type=1
"""

from __future__ import annotations

import json
import sys

from _returns_api_runner import run_returns_api
from _shopee_returns_common import emit_result, lf_inline_flag


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: get_reverse_tracking_info.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    inline = lf_inline_flag()
    emit_result(run_returns_api("get_reverse_tracking_info", params, "get_reverse_tracking_info.py"), inline)


if __name__ == "__main__":
    main()
