#!/usr/bin/env python3
"""Shopee 直播 get_latest_comment_list；定义见 references/api.md。"""
from _livestream_api_runner import cli


def main() -> None:
    cli('get_latest_comment_list')


if __name__ == "__main__":
    main()
