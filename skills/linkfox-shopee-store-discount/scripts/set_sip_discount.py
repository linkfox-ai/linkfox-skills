#!/usr/bin/env python3
"""Shopee set_sip_discount，参数与响应见 references/apis/set-sip-discount.md。"""
from _shopee_discount_common import discount_cli


def main() -> None:
    discount_cli("set_sip_discount")


if __name__ == "__main__":
    main()
