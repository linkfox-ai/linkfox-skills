#!/usr/bin/env python3
"""
Shopee Store — upload_video_part

官方: https://open.shopee.com/documents/v2/v2.media.upload_video_part?module=130&type=1

入参说明见 references/apis/upload-video-part.md。
"""

from __future__ import annotations

import json
import sys

from _media_api_runner import run_media_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: upload_video_part.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    run_media_api("upload_video_part", params, "upload_video_part.py")


if __name__ == "__main__":
    main()
