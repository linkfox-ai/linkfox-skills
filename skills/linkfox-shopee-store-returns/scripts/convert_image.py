#!/usr/bin/env python3
"""Shopee 店铺 — 转换凭证图片（convert_image）。

官方：https://open.shopee.com/documents/v2/v2.returns.convert_image?module=102&type=1
入参与响应见 references/apis/convert-image.md。
"""

from _returns_api_runner import run_cli


def main() -> None:
    run_cli("convert_image")


if __name__ == "__main__":
    main()
