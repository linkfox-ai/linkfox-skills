#!/usr/bin/env python3
"""极目亚马逊关键词细分市场查询。

用法：
  python jiimore_get_niche_info_by_keyword.py '<JSON 参数>' [--inline] [--no-cache]

完整响应始终落盘；不超过 8 KB 时全量输出，否则输出摘要。
提供单层 24 小时参数缓存，--no-cache 禁用缓存，--inline 强制全量输出。
"""

from call_api import run


API_PATH = "/jiimore/getNicheInfoByKeyword"
SLUG = "linkfox-jiimore-get-niche-info-by-keyword"


def main():
    run(API_PATH, SLUG)


if __name__ == "__main__":
    main()
