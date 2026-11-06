#!/usr/bin/env python3
"""GeekBI Temu 店铺搜索入口，支持 JSON、--inline 与 --no-cache 用法。"""

from _geekbi_temu_shop import run_endpoint

API_PATH = "/geekbi/temu/mallSearch"


def main(argv=None):
    return run_endpoint(API_PATH, argv)


if __name__ == "__main__":
    main()
