#!/usr/bin/env python3
"""Shopee 店铺 — 提出解决方案（offer）。

官方：https://open.shopee.com/documents/v2/v2.returns.offer?module=102&type=1
入参与响应见 references/apis/offer.md。
"""

from _returns_api_runner import run_cli


def main() -> None:
    run_cli("offer")


if __name__ == "__main__":
    main()
