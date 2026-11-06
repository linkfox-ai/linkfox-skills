#!/usr/bin/env python3
"""Shopee AMS：终止定向推广活动。

官方: https://open.shopee.com/documents/v2/v2.ams.terminate_targeted_campaign?module=127&type=1
入参说明见 references/apis/terminate-targeted-campaign.md。
"""
from _ams_api_runner import cli_main

def main():
    cli_main("terminate_targeted_campaign")

if __name__ == "__main__":
    main()
