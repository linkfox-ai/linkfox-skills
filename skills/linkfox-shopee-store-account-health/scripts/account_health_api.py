#!/usr/bin/env python3
"""
Shopee 店铺账户健康通用查询入口
================================================

用法：
  python account_health_api.py '{"api": "get_shop_performance", "shopId": "67890"}'

官方文档： https://open.shopee.com/documents/v2/v2.account_health.<api>?module=103&type=1
"""

from _account_health_api_runner import account_health_cli


def main() -> None:
    account_health_cli()


if __name__ == "__main__":
    main()
