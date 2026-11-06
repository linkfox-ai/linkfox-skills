#!/usr/bin/env python3
"""Kalodata TikTok 达人详情。

用法：python kalodata_creator_detail.py '<JSON 参数>' [--inline] [--no-cache]
提供 24 小时本地缓存；完整响应始终落盘，大响应默认只输出摘要。
"""

from _creator_common import run_creator


API_PATH = "/kalodata/creator/detail"


def main():
    run_creator(API_PATH)


if __name__ == "__main__":
    main()
