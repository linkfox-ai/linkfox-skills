#!/usr/bin/env python3
"""
Shopee 店铺账户健康 — get_shop_performance (v2.account_health.get_shop_performance)

官方: https://open.shopee.com/documents/v2/v2.account_health.get_shop_performance?module=103&type=1

入参说明见 references/apis/get-shop-performance.md。

用法：
  python get_shop_performance.py '{"shopId":"67890"}'
"""

from _account_health_api_runner import account_health_cli


def main() -> None:
    account_health_cli('get_shop_performance')


if __name__ == "__main__":
    main()
