#!/usr/bin/env python3
"""
Shopee Store — edit_manual_product_ads (v2.ads.edit_manual_product_ads)
官方: https://open.shopee.com/documents/v2/v2.ads.edit_manual_product_ads?module=117&type=1
"""

from __future__ import annotations
from _shopee_ads_common import emit_result, lf_inline_flag

import json
import sys

from _ads_api_runner import run_ads_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: edit_manual_product_ads.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    inline = lf_inline_flag()
    emit_result(run_ads_api("edit_manual_product_ads", params, "edit_manual_product_ads.py"), inline)


if __name__ == "__main__":
    main()
