#!/usr/bin/env python3
"""Shopee 折扣通用入口，JSON 中 api 选择 12 项 Discount 操作。"""
from _shopee_discount_common import discount_cli


def main() -> None:
    discount_cli()


if __name__ == "__main__":
    main()
