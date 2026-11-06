#!/usr/bin/env python3
"""Shopee AMS：更新新品自动加入设置。

官方: https://open.shopee.com/documents/v2/v2.ams.update_auto_add_new_product_setting?module=127&type=1
入参说明见 references/apis/update-auto-add-new-product-setting.md。
"""
from _ams_api_runner import cli_main

def main():
    cli_main("update_auto_add_new_product_setting")

if __name__ == "__main__":
    main()
