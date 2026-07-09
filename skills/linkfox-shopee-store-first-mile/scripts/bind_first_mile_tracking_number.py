#!/usr/bin/env python3
"""
Shopee Store — bind_first_mile_tracking_number (v2.first_mile.bind_first_mile_tracking_number)
官方: https://open.shopee.com/documents/v2/v2.first_mile.bind_first_mile_tracking_number?module=96&type=1
"""

from __future__ import annotations

import json
import sys

from _first_mile_api_runner import run_first_mile_api
from _shopee_first_mile_common import emit_result, lf_inline_flag


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: bind_first_mile_tracking_number.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    inline = lf_inline_flag()
    emit_result(run_first_mile_api("bind_first_mile_tracking_number", params, "bind_first_mile_tracking_number.py"), inline)


if __name__ == "__main__":
    main()
