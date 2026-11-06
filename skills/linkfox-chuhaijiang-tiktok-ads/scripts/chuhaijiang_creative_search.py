#!/usr/bin/env python3
"""出海匠创意搜索；支持 JSON、--inline 和 --no-cache CLI。"""

from _chuhaijiang import main as run_business

API_PATH = "/chuhaijiang/ad-creative/creatives/search"


def main():
    run_business(API_PATH)


if __name__ == "__main__":
    main()
