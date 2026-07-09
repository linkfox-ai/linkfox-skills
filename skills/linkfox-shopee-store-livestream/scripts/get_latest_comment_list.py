#!/usr/bin/env python3
"""
Shopee Store — get_latest_comment_list (v2.livestream.get_latest_comment_list)
官方: https://open.shopee.com/documents/v2/v2.livestream.get_latest_comment_list?module=125&type=1
"""

from __future__ import annotations

import json
import sys

from _livestream_api_runner import run_livestream_api
from _shopee_livestream_common import emit_result, lf_inline_flag


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: get_latest_comment_list.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    inline = lf_inline_flag()
    emit_result(run_livestream_api("get_latest_comment_list", params, "get_latest_comment_list.py"), inline)


if __name__ == "__main__":
    main()
