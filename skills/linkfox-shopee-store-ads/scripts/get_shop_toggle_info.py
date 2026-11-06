#!/usr/bin/env python3
"""Shopee 店铺广告：get_shop_toggle_info。

官方：https://open.shopee.com/documents/v2/v2.ads.get_shop_toggle_info?module=117&type=1
入参与响应见 references/apis/get-shop-toggle-info.md。
用法：python scripts/get_shop_toggle_info.py '<JSON 参数>' [--inline] [--no-cache]
"""
from _ads_api_runner import cli_main


def main() -> None:
    cli_main("get_shop_toggle_info")


if __name__ == "__main__":
    main()
