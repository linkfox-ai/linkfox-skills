#!/usr/bin/env python3
"""
Shopee 店铺账户健康 — get_punishment_history (v2.account_health.get_punishment_history)

官方: https://open.shopee.com/documents/v2/v2.account_health.get_punishment_history?module=103&type=1

入参说明见 references/apis/get-punishment-history.md。

用法：
  python get_punishment_history.py '{"shopId":"67890","punishment_status":1,"page_size":20}'
"""

from _account_health_api_runner import account_health_cli


def main() -> None:
    account_health_cli('get_punishment_history')


if __name__ == "__main__":
    main()
