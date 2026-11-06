#!/usr/bin/env python3
"""Shopee 店铺 — 查询争议原因（get_return_dispute_reason）。

官方：https://open.shopee.com/documents/v2/v2.returns.get_return_dispute_reason?module=102&type=1
入参与响应见 references/apis/get-return-dispute-reason.md。
"""

from _returns_api_runner import run_cli


def main() -> None:
    run_cli("get_return_dispute_reason")


if __name__ == "__main__":
    main()
