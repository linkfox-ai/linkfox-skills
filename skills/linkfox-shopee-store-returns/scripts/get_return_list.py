#!/usr/bin/env python3
"""Shopee 店铺 — 查询退货退款列表（get_return_list）。

官方：https://open.shopee.com/documents/v2/v2.returns.get_return_list?module=102&type=1
入参与响应见 references/apis/get-return-list.md。
"""

from _returns_api_runner import run_cli


def main() -> None:
    run_cli("get_return_list")


if __name__ == "__main__":
    main()
