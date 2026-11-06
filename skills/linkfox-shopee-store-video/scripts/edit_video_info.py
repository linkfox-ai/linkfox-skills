#!/usr/bin/env python3
"""
Shopee Store — edit_video_info

官方: https://open.shopee.com/documents/v2/v2.video.edit_video_info?module=129&type=1

入参说明见 references/apis/edit-video-info.md。
"""

from __future__ import annotations

import json
import sys

from _video_api_runner import emit_result, lf_inline_flag, run_video_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: edit_video_info.py '<JSON>' [--inline] [--no-cache]", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    emit_result(run_video_api("edit_video_info", params, "edit_video_info.py"), slug="linkfox-shopee-store-video-edit_video_info", inline=lf_inline_flag())


if __name__ == "__main__":
    main()
