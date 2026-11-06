#!/usr/bin/env python3
"""
Shopee Store — get_video_upload_result

官方: https://open.shopee.com/documents/v2/v2.media.get_video_upload_result?module=130&type=1

入参说明见 references/apis/get-video-upload-result.md。
"""

from __future__ import annotations

import json
import sys

from _media_api_runner import run_media_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: get_video_upload_result.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    run_media_api("get_video_upload_result", params, "get_video_upload_result.py")


if __name__ == "__main__":
    main()
