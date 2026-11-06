#!/usr/bin/env python3
"""Shopee 店铺 — 查询退货承运商（get_shipping_carrier）。

官方：https://open.shopee.com/documents/v2/v2.returns.get_shipping_carrier?module=102&type=1
入参与响应见 references/apis/get-shipping-carrier.md。
"""

from _returns_api_runner import run_cli


def main() -> None:
    run_cli("get_shipping_carrier")


if __name__ == "__main__":
    main()
