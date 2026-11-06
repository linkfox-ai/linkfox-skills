#!/usr/bin/env python3
"""Kalodata 单店详情 CLI：JSON 参数，支持 --inline 与 --no-cache。"""

from _kalodata_shop_common import main as _main

API_PATH = "/kalodata/shop/detail"


def main():
    return _main(API_PATH)


if __name__ == "__main__":
    raise SystemExit(main())
