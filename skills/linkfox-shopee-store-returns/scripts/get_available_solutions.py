#!/usr/bin/env python3
"""
Shopee Store — get_available_solutions (v2.returns.get_available_solutions)
官方: https://open.shopee.com/documents/v2/v2.returns.get_available_solutions?module=102&type=1
"""

from __future__ import annotations

import json
import sys

from _returns_api_runner import run_returns_api
from _shopee_returns_common import emit_result, lf_inline_flag


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: get_available_solutions.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    inline = lf_inline_flag()
    emit_result(run_returns_api("get_available_solutions", params, "get_available_solutions.py"), inline)


if __name__ == "__main__":
    main()
