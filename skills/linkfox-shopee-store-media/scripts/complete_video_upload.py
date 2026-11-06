#!/usr/bin/env python3
"""
Shopee Store — complete_video_upload

官方: https://open.shopee.com/documents/v2/v2.media.complete_video_upload?module=130&type=1

入参说明见 references/apis/complete-video-upload.md。
"""

from __future__ import annotations

import json
import sys

from _media_api_runner import run_media_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: complete_video_upload.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    run_media_api("complete_video_upload", params, "complete_video_upload.py")


if __name__ == "__main__":
    main()
