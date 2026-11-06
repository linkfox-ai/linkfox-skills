#!/usr/bin/env python3
"""Shopee AMS：编辑定向推广商品列表。

官方: https://open.shopee.com/documents/v2/v2.ams.edit_product_list_of_targeted_campaign?module=127&type=1
入参说明见 references/apis/edit-product-list-of-targeted-campaign.md。
"""
from _ams_api_runner import cli_main

def main():
    cli_main("edit_product_list_of_targeted_campaign")

if __name__ == "__main__":
    main()
