#!/usr/bin/env python3
"""Shopee AMS：批量移除开放推广商品。

官方: https://open.shopee.com/documents/v2/v2.ams.batch_remove_products_open_campaign_setting?module=127&type=1
入参说明见 references/apis/batch-remove-products-open-campaign-setting.md。
"""
from _ams_api_runner import cli_main

def main():
    cli_main("batch_remove_products_open_campaign_setting")

if __name__ == "__main__":
    main()
