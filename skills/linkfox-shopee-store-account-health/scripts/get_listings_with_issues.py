#!/usr/bin/env python3
"""
Shopee 店铺账户健康 — get_listings_with_issues (v2.account_health.get_listings_with_issues)

官方: https://open.shopee.com/documents/v2/v2.account_health.get_listings_with_issues?module=103&type=1

入参说明见 references/apis/get-listings-with-issues.md。

用法：
  python get_listings_with_issues.py '{"shopId":"67890","page_no":1,"page_size":50}'
"""

from _account_health_api_runner import account_health_cli


def main() -> None:
    account_health_cli('get_listings_with_issues')


if __name__ == "__main__":
    main()
