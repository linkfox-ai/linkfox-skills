#!/usr/bin/env python3
"""
Shopee 商户 — get_merchant_info

官方: https://open.shopee.com/documents/v2/v2.merchant.get_merchant_info?module=93&type=1

入参说明见 references/apis/get-merchant-info.md。
"""

from _merchant_api_runner import merchant_cli


def main() -> None:
    merchant_cli('get_merchant_info', 'get_merchant_info.py')


if __name__ == "__main__":
    main()
