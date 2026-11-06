#!/usr/bin/env python3
"""Shopee 店铺 — 取消退货争议（cancel_dispute）。

官方：https://open.shopee.com/documents/v2/v2.returns.cancel_dispute?module=102&type=1
入参与响应见 references/apis/cancel-dispute.md。
"""

from _returns_api_runner import run_cli


def main() -> None:
    run_cli("cancel_dispute")


if __name__ == "__main__":
    main()
