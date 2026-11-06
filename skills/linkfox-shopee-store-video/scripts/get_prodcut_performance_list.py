#!/usr/bin/env python3
"""
Shopee Store — get_prodcut_performance_list

官方: https://open.shopee.com/documents/v2/v2.video.get_prodcut_performance_list?module=129&type=1

入参说明见 references/apis/get-prodcut-performance-list.md。
"""

from __future__ import annotations

import json
import sys

from _video_api_runner import emit_result, lf_inline_flag, run_video_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: get_prodcut_performance_list.py '<JSON>' [--inline] [--no-cache]", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    emit_result(run_video_api("get_prodcut_performance_list", params, "get_prodcut_performance_list.py"), slug="linkfox-shopee-store-video-get_prodcut_performance_list", inline=lf_inline_flag())


if __name__ == "__main__":
    main()
