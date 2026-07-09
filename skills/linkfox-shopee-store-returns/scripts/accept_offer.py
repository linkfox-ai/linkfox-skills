#!/usr/bin/env python3
"""
Shopee Store — accept_offer (v2.returns.accept_offer)
官方: https://open.shopee.com/documents/v2/v2.returns.accept_offer?module=102&type=1
"""

from __future__ import annotations

import json
import sys

from _returns_api_runner import run_returns_api
from _shopee_returns_common import emit_result, lf_inline_flag


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: accept_offer.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    inline = lf_inline_flag()
    emit_result(run_returns_api("accept_offer", params, "accept_offer.py"), inline)


if __name__ == "__main__":
    main()
