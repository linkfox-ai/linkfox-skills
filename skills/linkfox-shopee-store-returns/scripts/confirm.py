#!/usr/bin/env python3
"""Shopee 店铺 — 确认退货（confirm）。

官方：https://open.shopee.com/documents/v2/v2.returns.confirm?module=102&type=1
入参与响应见 references/apis/confirm.md。
"""

from _returns_api_runner import run_cli


def main() -> None:
    run_cli("confirm")


if __name__ == "__main__":
    main()
