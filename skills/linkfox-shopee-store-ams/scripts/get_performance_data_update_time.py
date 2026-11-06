#!/usr/bin/env python3
"""Shopee AMS：查询效果数据更新时间。

官方: https://open.shopee.com/documents/v2/v2.ams.get_performance_data_update_time?module=127&type=1
入参说明见 references/apis/get-performance-data-update-time.md。
"""
from _ams_api_runner import cli_main

def main():
    cli_main("get_performance_data_update_time")

if __name__ == "__main__":
    main()
