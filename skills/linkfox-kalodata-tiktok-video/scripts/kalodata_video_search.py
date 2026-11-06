#!/usr/bin/env python3
"""Kalodata TikTok 视频榜单；位置参数为 JSON，支持 --inline 和 --no-cache。"""

import sys
from _kalodata_video_common import run_video

API_PATH = "/kalodata/video/rank"


def main(argv=None):
    return run_video(API_PATH, "rank", argv)


if __name__ == "__main__":
    sys.exit(main())
