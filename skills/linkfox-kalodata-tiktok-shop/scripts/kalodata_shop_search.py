#!/usr/bin/env python3
"""Kalodata 店铺榜单 CLI：JSON 参数，支持 --inline 与 --no-cache。"""

from _kalodata_shop_common import main as _main

API_PATH = "/kalodata/shop/rank"


def main():
    return _main(API_PATH)


if __name__ == "__main__":
    raise SystemExit(main())
