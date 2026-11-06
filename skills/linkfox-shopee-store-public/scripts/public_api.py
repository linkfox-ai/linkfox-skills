#!/usr/bin/env python3
"""Shopee Public 通用入口；JSON 中的 api 选择六个 Public 操作。"""

from _public_api_runner import invoke_public_cli


def main() -> None:
    invoke_public_cli()


if __name__ == "__main__":
    main()
