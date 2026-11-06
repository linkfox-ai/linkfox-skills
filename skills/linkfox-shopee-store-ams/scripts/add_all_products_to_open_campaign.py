#!/usr/bin/env python3
"""Shopee AMS：将全部合格商品加入开放推广。

官方: https://open.shopee.com/documents/v2/v2.ams.add_all_products_to_open_campaign?module=127&type=1
入参说明见 references/apis/add-all-products-to-open-campaign.md。
"""
from _ams_api_runner import cli_main

def main():
    cli_main("add_all_products_to_open_campaign")

if __name__ == "__main__":
    main()
