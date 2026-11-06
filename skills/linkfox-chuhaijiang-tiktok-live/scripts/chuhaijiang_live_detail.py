#!/usr/bin/env python3
"""出海匠 TikTok 直播详情；用法见 --help。"""

from _chuhaijiang_live_common import main as run_live

API_PATH = "/chuhaijiang/lives/detail"


def main(argv=None):
    run_live(API_PATH, argv)


if __name__ == "__main__":
    main()
