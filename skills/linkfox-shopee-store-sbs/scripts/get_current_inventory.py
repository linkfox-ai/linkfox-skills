#!/usr/bin/env python3
"""
Shopee Store — get_current_inventory (v2.sbs.get_current_inventory)
官方: https://open.shopee.com/documents/v2/v2.sbs.get_current_inventory?module=124&type=1
"""

from __future__ import annotations

import json
import sys

from _sbs_api_runner import emit_result, lf_inline_flag, run_sbs_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: get_current_inventory.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    inline = lf_inline_flag()
    emit_result(run_sbs_api("get_current_inventory", params, "get_current_inventory.py"), inline)


if __name__ == "__main__":
    main()
