#!/usr/bin/env python3
"""Shopee AMS：查询结算验证报告。

官方: https://open.shopee.com/documents/v2/v2.ams.get_validation_report?module=127&type=1
入参说明见 references/apis/get-validation-report.md。
"""
from _ams_api_runner import cli_main

def main():
    cli_main("get_validation_report")

if __name__ == "__main__":
    main()
