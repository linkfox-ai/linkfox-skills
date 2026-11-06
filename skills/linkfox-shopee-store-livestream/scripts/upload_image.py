#!/usr/bin/env python3
"""Shopee 直播 upload_image；定义见 references/api.md。"""
from _livestream_api_runner import cli


def main() -> None:
    cli('upload_image')


if __name__ == "__main__":
    main()
