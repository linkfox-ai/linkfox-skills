#!/usr/bin/env python3
"""
Shopee Store — get_product_level_campaign_id_list (v2.ads.get_product_level_campaign_id_list)
官方: https://open.shopee.com/documents/v2/v2.ads.get_product_level_campaign_id_list?module=117&type=1
"""

from __future__ import annotations
from _shopee_ads_common import emit_result, lf_inline_flag

import json
import sys

from _ads_api_runner import run_ads_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: get_product_level_campaign_id_list.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    inline = lf_inline_flag()
    emit_result(run_ads_api("get_product_level_campaign_id_list", params, "get_product_level_campaign_id_list.py"), inline)


if __name__ == "__main__":
    main()
