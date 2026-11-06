#!/usr/bin/env python3
"""Shopee 店铺 — 查询退货退款详情（get_return_detail）。

官方：https://open.shopee.com/documents/v2/v2.returns.get_return_detail?module=102&type=1
入参与响应见 references/apis/get-return-detail.md。
"""

from _returns_api_runner import run_cli


def main() -> None:
    run_cli("get_return_detail")


if __name__ == "__main__":
    main()
