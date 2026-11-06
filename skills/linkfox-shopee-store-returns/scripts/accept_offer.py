#!/usr/bin/env python3
"""Shopee 店铺 — 接受解决方案（accept_offer）。

官方：https://open.shopee.com/documents/v2/v2.returns.accept_offer?module=102&type=1
入参与响应见 references/apis/accept-offer.md。
"""

from _returns_api_runner import run_cli


def main() -> None:
    run_cli("accept_offer")


if __name__ == "__main__":
    main()
