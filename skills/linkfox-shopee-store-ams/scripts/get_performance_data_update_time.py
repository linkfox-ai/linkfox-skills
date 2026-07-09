#!/usr/bin/env python3
"""
Shopee Store — get_performance_data_update_time (v2.ams.get_performance_data_update_time)
官方: https://open.shopee.com/documents/v2/v2.ams.get_performance_data_update_time?module=127&type=1
"""

from __future__ import annotations
from _shopee_ams_common import emit_result, lf_inline_flag

import json
import sys

from _ams_api_runner import run_ams_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: get_performance_data_update_time.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    inline = lf_inline_flag()
    emit_result(run_ams_api("get_performance_data_update_time", params, "get_performance_data_update_time.py"), inline)


if __name__ == "__main__":
    main()
