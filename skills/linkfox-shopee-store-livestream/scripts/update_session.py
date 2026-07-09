#!/usr/bin/env python3
"""
Shopee Store — update_session (v2.livestream.update_session)
官方: https://open.shopee.com/documents/v2/v2.livestream.update_session?module=125&type=1
"""

from __future__ import annotations

import json
import sys

from _livestream_api_runner import run_livestream_api
from _shopee_livestream_common import emit_result, lf_inline_flag


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: update_session.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    inline = lf_inline_flag()
    emit_result(run_livestream_api("update_session", params, "update_session.py"), inline)


if __name__ == "__main__":
    main()
