#!/usr/bin/env python3
"""Kalodata TikTok 视频详情；位置参数为 JSON，支持 --inline 和 --no-cache。"""

import sys
from _kalodata_video_common import run_video

API_PATH = "/kalodata/video/detail"


def main(argv=None):
    return run_video(API_PATH, "detail", argv)


if __name__ == "__main__":
    sys.exit(main())
