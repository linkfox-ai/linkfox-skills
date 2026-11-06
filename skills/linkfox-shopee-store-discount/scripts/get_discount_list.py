#!/usr/bin/env python3
"""Shopee get_discount_list，参数与响应见 references/apis/get-discount-list.md。"""
from _shopee_discount_common import discount_cli


def main() -> None:
    discount_cli("get_discount_list")


if __name__ == "__main__":
    main()
