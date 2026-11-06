#!/usr/bin/env python3
"""全球站广告操作的 CLI 入口。"""

import sys

import _temu_global_common  # noqa: F401 — gateway helpers in scripts/

from _temu_common import load_json_arg
from _temu_global_common import extract_business_params, run_and_print

def run_cli(api_type: str, usage: str) -> None:
    if len(sys.argv) < 2:
        print(f"Usage: {usage}", file=sys.stderr)
        sys.exit(1)
    params = load_json_arg(sys.argv)
    run_and_print(params, api_type, extract_business_params(params))
