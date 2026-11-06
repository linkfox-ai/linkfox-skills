#!/usr/bin/env python3
"""Shopee 店铺广告：get_gms_campaign_performance。

官方：https://open.shopee.com/documents/v2/v2.ads.get_gms_campaign_performance?module=117&type=1
入参与响应见 references/apis/get-gms-campaign-performance.md。
用法：python scripts/get_gms_campaign_performance.py '<JSON 参数>' [--inline] [--no-cache]
"""
from _ads_api_runner import cli_main


def main() -> None:
    cli_main("get_gms_campaign_performance")


if __name__ == "__main__":
    main()
