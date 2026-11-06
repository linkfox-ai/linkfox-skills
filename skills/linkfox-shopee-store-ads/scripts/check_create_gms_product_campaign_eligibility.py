#!/usr/bin/env python3
"""Shopee 店铺广告：check_create_gms_product_campaign_eligibility。

官方：https://open.shopee.com/documents/v2/v2.ads.check_create_gms_product_campaign_eligibility?module=117&type=1
入参与响应见 references/apis/check-create-gms-product-campaign-eligibility.md。
用法：python scripts/check_create_gms_product_campaign_eligibility.py '<JSON 参数>' [--inline] [--no-cache]
"""
from _ads_api_runner import cli_main


def main() -> None:
    cli_main("check_create_gms_product_campaign_eligibility")


if __name__ == "__main__":
    main()
