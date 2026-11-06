#!/usr/bin/env python3
"""
Shopee Store — delete_video

官方: https://open.shopee.com/documents/v2/v2.video.delete_video?module=129&type=1

入参说明见 references/apis/delete-video.md。
"""

from __future__ import annotations

import json
import sys

from _video_api_runner import emit_result, lf_inline_flag, run_video_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: delete_video.py '<JSON>' [--inline] [--no-cache]", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    emit_result(run_video_api("delete_video", params, "delete_video.py"), slug="linkfox-shopee-store-video-delete_video", inline=lf_inline_flag())


if __name__ == "__main__":
    main()
