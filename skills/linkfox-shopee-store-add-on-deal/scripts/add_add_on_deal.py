#!/usr/bin/env python3
"""
Shopee Store — add_add_on_deal (v2.add_on_deal.add_add_on_deal)
官方: https://open.shopee.com/documents/v2/v2.add_on_deal.add_add_on_deal?module=111&type=1
"""

from __future__ import annotations
from _shopee_add_on_deal_common import emit_result, lf_inline_flag

import json
import sys

from _add_on_deal_api_runner import run_add_on_deal_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: add_add_on_deal.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    inline = lf_inline_flag()
    emit_result(run_add_on_deal_api("add_add_on_deal", params, "add_add_on_deal.py"), inline)


if __name__ == "__main__":
    main()
