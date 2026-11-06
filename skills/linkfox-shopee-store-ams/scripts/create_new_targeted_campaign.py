#!/usr/bin/env python3
"""Shopee AMS：创建定向推广活动。

官方: https://open.shopee.com/documents/v2/v2.ams.create_new_targeted_campaign?module=127&type=1
入参说明见 references/apis/create-new-targeted-campaign.md。
"""
from _ams_api_runner import cli_main

def main():
    cli_main("create_new_targeted_campaign")

if __name__ == "__main__":
    main()
