#!/usr/bin/env python3
"""Shopee AMS：查询达人效果。

官方: https://open.shopee.com/documents/v2/v2.ams.get_affiliate_performance?module=127&type=1
入参说明见 references/apis/get-affiliate-performance.md。
"""
from _ams_api_runner import cli_main

def main():
    cli_main("get_affiliate_performance")

if __name__ == "__main__":
    main()
