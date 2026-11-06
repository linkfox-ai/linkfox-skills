#!/usr/bin/env python3
"""Shopee 直播 create_session；定义见 references/api.md。"""
from _livestream_api_runner import cli


def main() -> None:
    cli('create_session')


if __name__ == "__main__":
    main()
