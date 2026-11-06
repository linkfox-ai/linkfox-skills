#!/usr/bin/env python3
"""Shopee 店铺广告：edit_manual_product_ad_keywords。

官方：https://open.shopee.com/documents/v2/v2.ads.edit_manual_product_ad_keywords?module=117&type=1
入参与响应见 references/apis/edit-manual-product-ad-keywords.md。
用法：python scripts/edit_manual_product_ad_keywords.py '<JSON 参数>' [--inline] [--no-cache]
"""
from _ads_api_runner import cli_main


def main() -> None:
    cli_main("edit_manual_product_ad_keywords")


if __name__ == "__main__":
    main()
