#!/usr/bin/env python3
"""Shopee AMS：查询推荐达人。

官方: https://open.shopee.com/documents/v2/v2.ams.get_recommended_affiliate_list?module=127&type=1
入参说明见 references/apis/get-recommended-affiliate-list.md。
"""
from _ams_api_runner import cli_main

def main():
    cli_main("get_recommended_affiliate_list")

if __name__ == "__main__":
    main()
