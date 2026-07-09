#!/usr/bin/env python3
"""
Shopee Store — update_top_picks (v2.top_picks.update_top_picks)
官方: https://open.shopee.com/documents/v2/v2.top_picks.update_top_picks?module=100&type=1
"""

from __future__ import annotations

import json
import sys

from _top_picks_api_runner import emit_result, lf_inline_flag, run_top_picks_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: update_top_picks.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    inline = lf_inline_flag()
    emit_result(run_top_picks_api("update_top_picks", params, "update_top_picks.py"), inline)


if __name__ == "__main__":
    main()
