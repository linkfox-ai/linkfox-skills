#!/usr/bin/env python3
"""GeekBI Temu siteList；接受 JSON、--inline 与 --no-cache 命令行参数。"""

from _geekbi_common import run

API_PATH = "/geekbi/temu/siteList"


def main():
    run(API_PATH)


if __name__ == "__main__":
    main()
