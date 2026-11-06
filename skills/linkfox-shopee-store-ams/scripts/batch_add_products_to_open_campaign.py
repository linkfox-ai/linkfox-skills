#!/usr/bin/env python3
"""Shopee AMS：批量添加开放推广商品。

官方: https://open.shopee.com/documents/v2/v2.ams.batch_add_products_to_open_campaign?module=127&type=1
入参说明见 references/apis/batch-add-products-to-open-campaign.md。
"""
from _ams_api_runner import cli_main

def main():
    cli_main("batch_add_products_to_open_campaign")

if __name__ == "__main__":
    main()
