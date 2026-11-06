#!/usr/bin/env python3
"""Shopee AMS：查询未加入开放推广的商品。

官方: https://open.shopee.com/documents/v2/v2.ams.get_open_campaign_not_added_product?module=127&type=1
入参说明见 references/apis/get-open-campaign-not-added-product.md。
"""
from _ams_api_runner import cli_main

def main():
    cli_main("get_open_campaign_not_added_product")

if __name__ == "__main__":
    main()
