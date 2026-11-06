#!/usr/bin/env python3
"""
Seerfar Ozon Category Search - LinkFox Skill
调用 /seerfar/ozon/categorySearch 接口。

Usage:
  python seerfar_ozon_category_search.py '<JSON parameters>' [--inline] [--no-cache]

完整响应始终落盘；不超过 8 KB 时全量输出，否则输出摘要。
--inline 强制全量输出，--no-cache 禁用默认的 24 小时本地缓存。
"""

from call_api import run


API_PATH = "/seerfar/ozon/categorySearch"
SLUG = "linkfox-seerfar-ozon-category-search"


def main():
    run(API_PATH, SLUG)


if __name__ == "__main__":
    main()
