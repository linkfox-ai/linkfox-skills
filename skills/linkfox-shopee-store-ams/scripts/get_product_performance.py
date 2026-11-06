#!/usr/bin/env python3
"""Shopee AMS：查询商品效果。

官方: https://open.shopee.com/documents/v2/v2.ams.get_product_performance?module=127&type=1
入参说明见 references/apis/get-product-performance.md。
"""
from _ams_api_runner import cli_main

def main():
    cli_main("get_product_performance")

if __name__ == "__main__":
    main()
