#!/usr/bin/env python3
"""Shopee 商户通用入口，保留 JSON 中 api 字段的调用方式。

用法：python merchant_api.py '{"api":"get_merchant_info","merchantId":"12345"}'
官方：https://open.shopee.com/documents/v2/v2.merchant.<api>?module=93&type=1
"""

from _merchant_api_runner import merchant_cli


def main() -> None:
    merchant_cli(caller="merchant_api.py")


if __name__ == "__main__":
    main()
