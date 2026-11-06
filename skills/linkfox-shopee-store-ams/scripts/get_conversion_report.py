#!/usr/bin/env python3
"""Shopee AMS：查询转化报告。

官方: https://open.shopee.com/documents/v2/v2.ams.get_conversion_report?module=127&type=1
入参说明见 references/apis/get-conversion-report.md。
"""
from _ams_api_runner import cli_main

def main():
    cli_main("get_conversion_report")

if __name__ == "__main__":
    main()
