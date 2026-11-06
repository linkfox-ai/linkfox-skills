#!/usr/bin/env python3
"""Shopee get_sip_discounts，参数与响应见 references/apis/get-sip-discounts.md。"""
from _shopee_discount_common import discount_cli


def main() -> None:
    discount_cli("get_sip_discounts")


if __name__ == "__main__":
    main()
