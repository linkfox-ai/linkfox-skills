#!/usr/bin/env python3
"""Shopee AMS：筛选查询达人列表。

官方: https://open.shopee.com/documents/v2/v2.ams.query_affiliate_list?module=127&type=1
入参说明见 references/apis/query-affiliate-list.md。
"""
from _ams_api_runner import cli_main

def main():
    cli_main("query_affiliate_list")

if __name__ == "__main__":
    main()
