#!/usr/bin/env python3
"""Kalodata TikTok 直播榜单。

用法：python kalodata_livestream_search.py '<JSON 参数>' [--inline] [--no-cache]
默认提供 24 小时缓存，始终保存完整响应；超过 8 KB 时打印摘要。
"""

from _livestream_runtime import run_livestream

API_PATH = "/kalodata/livestream/rank"
SLUG = "linkfox-kalodata-tiktok-livestream-rank"


def main():
    return run_livestream(API_PATH, SLUG)


if __name__ == "__main__":
    main()
