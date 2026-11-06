#!/usr/bin/env python3
"""Shopee AMS：查询商品优化建议。

官方: https://open.shopee.com/documents/v2/v2.ams.get_optimization_suggestion_product?module=127&type=1
入参说明见 references/apis/get-optimization-suggestion-product.md。
"""
from _ams_api_runner import cli_main

def main():
    cli_main("get_optimization_suggestion_product")

if __name__ == "__main__":
    main()
