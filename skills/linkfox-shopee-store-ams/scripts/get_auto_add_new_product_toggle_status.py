#!/usr/bin/env python3
"""Shopee AMS：查询新品自动加入开关。

官方: https://open.shopee.com/documents/v2/v2.ams.get_auto_add_new_product_toggle_status?module=127&type=1
入参说明见 references/apis/get-auto-add-new-product-toggle-status.md。
"""
from _ams_api_runner import cli_main

def main():
    cli_main("get_auto_add_new_product_toggle_status")

if __name__ == "__main__":
    main()
