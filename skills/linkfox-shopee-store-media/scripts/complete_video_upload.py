#!/usr/bin/env python3
"""
Shopee Store — complete_video_upload (v2.media.complete_video_upload)
官方: https://open.shopee.com/documents/v2/v2.media.complete_video_upload?module=130&type=1
"""

from __future__ import annotations

import json
import sys

from _media_api_runner import run_media_api
from _shopee_media_common import emit_result, lf_inline_flag


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: complete_video_upload.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    inline = lf_inline_flag()
    emit_result(run_media_api("complete_video_upload", params, "complete_video_upload.py"), inline)


if __name__ == "__main__":
    main()
