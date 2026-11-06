#!/usr/bin/env python3
"""GeekBI Temu 品类列表入口，支持 JSON、--inline 与 --no-cache 用法。"""

from _geekbi_temu_shop import run_endpoint

API_PATH = "/geekbi/temu/categoryList"


def main(argv=None):
    return run_endpoint(API_PATH, argv)


if __name__ == "__main__":
    main()
