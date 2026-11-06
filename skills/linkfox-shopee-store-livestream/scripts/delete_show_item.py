#!/usr/bin/env python3
"""Shopee 直播 delete_show_item；定义见 references/api.md。"""
from _livestream_api_runner import cli


def main() -> None:
    cli('delete_show_item')


if __name__ == "__main__":
    main()
