#!/usr/bin/env python3
"""Shopee delete_discount_item，参数与响应见 references/apis/delete-discount-item.md。"""
from _shopee_discount_common import discount_cli


def main() -> None:
    discount_cli("delete_discount_item")


if __name__ == "__main__":
    main()
