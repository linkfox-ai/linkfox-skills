#!/usr/bin/env python3
"""
Shopee 店铺账户健康 — get_late_orders (v2.account_health.get_late_orders)

官方: https://open.shopee.com/documents/v2/v2.account_health.get_late_orders?module=103&type=1

入参说明见 references/apis/get-late-orders.md。

用法：
  python get_late_orders.py '{"shopId":"67890","page_no":1,"page_size":20}'
"""

from _account_health_api_runner import account_health_cli


def main() -> None:
    account_health_cli('get_late_orders')


if __name__ == "__main__":
    main()
