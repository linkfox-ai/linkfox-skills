#!/usr/bin/env python3
"""Shopee AMS：更新定向推广基本信息。

官方: https://open.shopee.com/documents/v2/v2.ams.update_basic_info_of_targeted_campaign?module=127&type=1
入参说明见 references/apis/update-basic-info-of-targeted-campaign.md。
"""
from _ams_api_runner import cli_main

def main():
    cli_main("update_basic_info_of_targeted_campaign")

if __name__ == "__main__":
    main()
