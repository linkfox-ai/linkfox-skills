#!/usr/bin/env python3
"""欧洲站商品操作的 CLI 公共入口。"""

import sys

from _temu_common import load_json_arg
from _temu_eu_common import extract_business_params, run_and_print

def run_cli(api_type: str, usage: str) -> None:
    if len(sys.argv) < 2:
        print(f"Usage: {usage}", file=sys.stderr)
        sys.exit(1)
    params = load_json_arg(sys.argv)
    run_and_print(params, api_type, extract_business_params(params))
