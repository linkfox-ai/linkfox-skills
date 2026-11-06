#!/usr/bin/env python3
"""Shopee AMS：查询定向推广设置。

官方: https://open.shopee.com/documents/v2/v2.ams.get_targeted_campaign_settings?module=127&type=1
入参说明见 references/apis/get-targeted-campaign-settings.md。
"""
from _ams_api_runner import cli_main

def main():
    cli_main("get_targeted_campaign_settings")

if __name__ == "__main__":
    main()
