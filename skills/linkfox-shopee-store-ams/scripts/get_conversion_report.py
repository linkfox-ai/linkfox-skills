#!/usr/bin/env python3
"""
Shopee Store — get_conversion_report (v2.ams.get_conversion_report)
官方: https://open.shopee.com/documents/v2/v2.ams.get_conversion_report?module=127&type=1
"""

from __future__ import annotations
from _shopee_ams_common import emit_result, lf_inline_flag

import json
import sys

from _ams_api_runner import run_ams_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: get_conversion_report.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    inline = lf_inline_flag()
    emit_result(run_ams_api("get_conversion_report", params, "get_conversion_report.py"), inline)


if __name__ == "__main__":
    main()
