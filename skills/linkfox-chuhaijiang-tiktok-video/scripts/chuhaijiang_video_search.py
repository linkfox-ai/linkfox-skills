#!/usr/bin/env python3
"""出海匠视频业务入口；接受 JSON 参数、--inline 和 --no-cache。"""

from _chuhaijiang_video import SLUG, run

API_PATH = "/chuhaijiang/videos/search"


def main(argv=None):
    return run(API_PATH, argv)


if __name__ == "__main__":
    raise SystemExit(main())
