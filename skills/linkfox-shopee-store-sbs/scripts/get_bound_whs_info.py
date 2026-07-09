#!/usr/bin/env python3
"""
Shopee Store — get_bound_whs_info (v2.sbs.get_bound_whs_info)
官方: https://open.shopee.com/documents/v2/v2.sbs.get_bound_whs_info?module=124&type=1
"""

from __future__ import annotations

import json
import sys

from _sbs_api_runner import emit_result, lf_inline_flag, run_sbs_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: get_bound_whs_info.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    inline = lf_inline_flag()
    emit_result(run_sbs_api("get_bound_whs_info", params, "get_bound_whs_info.py"), inline)


if __name__ == "__main__":
    main()
