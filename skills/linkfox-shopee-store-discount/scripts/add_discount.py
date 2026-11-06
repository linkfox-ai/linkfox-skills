#!/usr/bin/env python3
"""Shopee add_discount，参数与响应见 references/apis/add-discount.md。"""
from _shopee_discount_common import discount_cli


def main() -> None:
    discount_cli("add_discount")


if __name__ == "__main__":
    main()
