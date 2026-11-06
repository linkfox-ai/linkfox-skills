#!/usr/bin/env python3
"""Shopee 直播 unban_user_comment；定义见 references/api.md。"""
from _livestream_api_runner import cli


def main() -> None:
    cli('unban_user_comment')


if __name__ == "__main__":
    main()
