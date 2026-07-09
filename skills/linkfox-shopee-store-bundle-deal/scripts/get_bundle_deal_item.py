#!/usr/bin/env python3
"""
Shopee Store — get_bundle_deal_item (v2.bundle_deal.get_bundle_deal_item)
官方: https://open.shopee.com/documents/v2/v2.bundle_deal.get_bundle_deal_item?module=110&type=1
"""

from __future__ import annotations
from _shopee_bundle_deal_common import emit_result, lf_inline_flag

import json
import sys

from _bundle_deal_api_runner import run_bundle_deal_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: get_bundle_deal_item.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    inline = lf_inline_flag()
    emit_result(run_bundle_deal_api("get_bundle_deal_item", params, "get_bundle_deal_item.py"), inline)


if __name__ == "__main__":
    main()
