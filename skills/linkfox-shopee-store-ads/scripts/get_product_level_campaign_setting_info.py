#!/usr/bin/env python3
"""Shopee 店铺广告：get_product_level_campaign_setting_info。

官方：https://open.shopee.com/documents/v2/v2.ads.get_product_level_campaign_setting_info?module=117&type=1
入参与响应见 references/apis/get-product-level-campaign-setting-info.md。
用法：python scripts/get_product_level_campaign_setting_info.py '<JSON 参数>' [--inline] [--no-cache]
"""
from _ads_api_runner import cli_main


def main() -> None:
    cli_main("get_product_level_campaign_setting_info")


if __name__ == "__main__":
    main()
