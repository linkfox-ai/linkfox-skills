#!/usr/bin/env python3
"""
Shopee Store — generic SBS API caller
======================================

Usage:
  python sbs_api.py '{"api": "get_bound_whs_info", "shopId": "67890"}'

Official docs: https://open.shopee.com/documents/v2/v2.sbs.<api>?module=124&type=1
"""

from __future__ import annotations

import json
import sys

from _sbs_api_runner import emit_result, lf_inline_flag, run_sbs_api
from _sbs_endpoints import list_api_names


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: sbs_api.py '<JSON with api field>'\nAvailable: {', '.join(list_api_names())}", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    if not params.get("api"):
        print("Missing required field: api", file=sys.stderr)
        sys.exit(1)
    inline = lf_inline_flag()
    emit_result(run_sbs_api(str(params["api"]), params, "sbs_api.py"), inline)


if __name__ == "__main__":
    main()
