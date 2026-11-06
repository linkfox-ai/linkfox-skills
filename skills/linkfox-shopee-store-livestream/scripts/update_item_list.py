#!/usr/bin/env python3
"""Shopee 直播 update_item_list；定义见 references/api.md。"""
from _livestream_api_runner import cli


def main() -> None:
    cli('update_item_list')


if __name__ == "__main__":
    main()
