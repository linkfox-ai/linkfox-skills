#!/usr/bin/env python3
"""
Shopee Store — delete_bundle_deal (v2.bundle_deal.delete_bundle_deal)
官方: https://open.shopee.com/documents/v2/v2.bundle_deal.delete_bundle_deal?module=110&type=1
"""

from __future__ import annotations
from _shopee_bundle_deal_common import emit_result, lf_inline_flag

import json
import sys

from _bundle_deal_api_runner import run_bundle_deal_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: delete_bundle_deal.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    inline = lf_inline_flag()
    emit_result(run_bundle_deal_api("delete_bundle_deal", params, "delete_bundle_deal.py"), inline)


if __name__ == "__main__":
    main()
