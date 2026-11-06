#!/usr/bin/env python3
"""Shopee 广告通用入口；JSON 必须包含 api 字段。

官方：https://open.shopee.com/documents/v2/v2.ads.<api>?module=117&type=1
用法：python scripts/ads_api.py '<含 api 的 JSON 参数>' [--inline] [--no-cache]
"""
from _ads_api_runner import cli_main


def main() -> None:
    cli_main()


if __name__ == "__main__":
    main()
