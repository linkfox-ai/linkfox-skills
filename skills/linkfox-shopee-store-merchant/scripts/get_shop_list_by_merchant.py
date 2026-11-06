#!/usr/bin/env python3
"""
Shopee 商户 — get_shop_list_by_merchant

官方: https://open.shopee.com/documents/v2/v2.merchant.get_shop_list_by_merchant?module=93&type=1

入参说明见 references/apis/get-shop-list-by-merchant.md。
"""

from _merchant_api_runner import merchant_cli


def main() -> None:
    merchant_cli('get_shop_list_by_merchant', 'get_shop_list_by_merchant.py')


if __name__ == "__main__":
    main()
