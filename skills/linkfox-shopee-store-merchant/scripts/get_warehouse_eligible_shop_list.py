#!/usr/bin/env python3
"""
Shopee 商户 — get_warehouse_eligible_shop_list

官方: https://open.shopee.com/documents/v2/v2.merchant.get_warehouse_eligible_shop_list?module=93&type=1

入参说明见 references/apis/get-warehouse-eligible-shop-list.md。
"""

from _merchant_api_runner import merchant_cli


def main() -> None:
    merchant_cli('get_warehouse_eligible_shop_list', 'get_warehouse_eligible_shop_list.py')


if __name__ == "__main__":
    main()
