#!/usr/bin/env python3
"""Shopee 店铺 — 查询可用解决方案（get_available_solutions）。

官方：https://open.shopee.com/documents/v2/v2.returns.get_available_solutions?module=102&type=1
入参与响应见 references/apis/get-available-solutions.md。
"""

from _returns_api_runner import run_cli


def main() -> None:
    run_cli("get_available_solutions")


if __name__ == "__main__":
    main()
