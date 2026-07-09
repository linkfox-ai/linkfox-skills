#!/usr/bin/env python3
"""
Shopee Store — cancel_video_upload (v2.media_space.cancel_video_upload)
官方: https://open.shopee.com/documents/v2/v2.media_space.cancel_video_upload?module=91&type=1
"""

from __future__ import annotations

import json
import sys

from _media_space_api_runner import run_media_space_api
from _shopee_media_space_common import emit_result, lf_inline_flag


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: cancel_video_upload.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    inline = lf_inline_flag()
    emit_result(run_media_space_api("cancel_video_upload", params, "cancel_video_upload.py"), inline)


if __name__ == "__main__":
    main()
