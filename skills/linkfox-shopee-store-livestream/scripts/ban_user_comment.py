#!/usr/bin/env python3
"""Shopee 直播 ban_user_comment；定义见 references/api.md。"""
from _livestream_api_runner import cli


def main() -> None:
    cli('ban_user_comment')


if __name__ == "__main__":
    main()
