#!/usr/bin/env python3
"""Shopee AMS 通用入口，JSON 必须含 api 字段。

官方: https://open.shopee.com/documents/v2/v2.ams.<api>?module=127&type=1
"""
from _ams_api_runner import cli_main

def main():
    cli_main()

if __name__ == "__main__":
    main()
