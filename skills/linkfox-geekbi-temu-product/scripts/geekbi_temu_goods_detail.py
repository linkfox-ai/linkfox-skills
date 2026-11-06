#!/usr/bin/env python3
"""GeekBI Temu 商品详情；支持 JSON、--inline 和 --no-cache 命令行。"""

from _geekbi_temu_common import main as run_workflow

API_PATH = "/geekbi/temu/goodsDetail"


def main():
    run_workflow(API_PATH)


if __name__ == "__main__":
    main()
