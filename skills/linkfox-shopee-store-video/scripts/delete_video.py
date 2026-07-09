#!/usr/bin/env python3
"""
Shopee Store — delete_video (v2.video.delete_video)
官方: https://open.shopee.com/documents/v2/v2.video.delete_video?module=129&type=1
"""

from __future__ import annotations

import json
import sys

from _video_api_runner import emit_result, lf_inline_flag, run_video_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: delete_video.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    inline = lf_inline_flag()
    emit_result(run_video_api("delete_video", params, "delete_video.py"), inline)


if __name__ == "__main__":
    main()
