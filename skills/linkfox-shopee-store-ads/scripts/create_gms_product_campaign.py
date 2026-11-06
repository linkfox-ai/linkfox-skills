#!/usr/bin/env python3
"""Shopee 店铺广告：create_gms_product_campaign。

官方：https://open.shopee.com/documents/v2/v2.ads.create_gms_product_campaign?module=117&type=1
入参与响应见 references/apis/create-gms-product-campaign.md。
用法：python scripts/create_gms_product_campaign.py '<JSON 参数>' [--inline] [--no-cache]
"""
from _ads_api_runner import cli_main


def main() -> None:
    cli_main("create_gms_product_campaign")


if __name__ == "__main__":
    main()
