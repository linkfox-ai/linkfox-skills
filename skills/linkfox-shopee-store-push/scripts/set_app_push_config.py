#!/usr/bin/env python3
"""
Shopee Store — set_app_push_config (v2.push.set_app_push_config)
官方: https://open.shopee.com/documents/v2/v2.push.set_app_push_config?module=105&type=1
"""

from __future__ import annotations

import json
import sys

from _push_api_runner import run_push_api
from _shopee_push_common import emit_result, lf_inline_flag


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: set_app_push_config.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    inline = lf_inline_flag()
    emit_result(run_push_api("set_app_push_config", params, "set_app_push_config.py"), inline)


if __name__ == "__main__":
    main()
