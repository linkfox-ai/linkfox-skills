#!/usr/bin/env python3
"""Shopee AMS：查询店铺建议佣金率。

官方: https://open.shopee.com/documents/v2/v2.ams.get_shop_suggested_rate?module=127&type=1
入参说明见 references/apis/get-shop-suggested-rate.md。
"""
from _ams_api_runner import cli_main

def main():
    cli_main("get_shop_suggested_rate")

if __name__ == "__main__":
    main()
