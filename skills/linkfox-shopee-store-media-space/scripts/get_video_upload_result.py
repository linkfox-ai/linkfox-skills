#!/usr/bin/env python3
"""
Shopee Store — get_video_upload_result (v2.media_space.get_video_upload_result)
官方: https://open.shopee.com/documents/v2/v2.media_space.get_video_upload_result?module=91&type=1
"""

from __future__ import annotations

import json
import sys

from _media_space_api_runner import run_media_space_api
from _shopee_media_space_common import emit_result, lf_inline_flag


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: get_video_upload_result.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    inline = lf_inline_flag()
    emit_result(run_media_space_api("get_video_upload_result", params, "get_video_upload_result.py"), inline)


if __name__ == "__main__":
    main()
