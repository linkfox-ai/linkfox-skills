#!/usr/bin/env python3
"""
Shopee Store — get_video_list (v2.video.get_video_list)
官方: https://open.shopee.com/documents/v2/v2.video.get_video_list?module=129&type=1
"""

from __future__ import annotations

import json
import sys

from _video_api_runner import emit_result, lf_inline_flag, run_video_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: get_video_list.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    inline = lf_inline_flag()
    emit_result(run_video_api("get_video_list", params, "get_video_list.py"), inline)


if __name__ == "__main__":
    main()
