#!/usr/bin/env python3
"""Shopee 店铺广告：get_create_product_ad_budget_suggestion。

官方：https://open.shopee.com/documents/v2/v2.ads.get_create_product_ad_budget_suggestion?module=117&type=1
入参与响应见 references/apis/get-create-product-ad-budget-suggestion.md。
用法：python scripts/get_create_product_ad_budget_suggestion.py '<JSON 参数>' [--inline] [--no-cache]
"""
from _ads_api_runner import cli_main


def main() -> None:
    cli_main("get_create_product_ad_budget_suggestion")


if __name__ == "__main__":
    main()
