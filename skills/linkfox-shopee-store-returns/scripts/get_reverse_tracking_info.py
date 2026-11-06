#!/usr/bin/env python3
"""Shopee 店铺 — 查询逆向物流轨迹（get_reverse_tracking_info）。

官方：https://open.shopee.com/documents/v2/v2.returns.get_reverse_tracking_info?module=102&type=1
入参与响应见 references/apis/get-reverse-tracking-info.md。
"""

from _returns_api_runner import run_cli


def main() -> None:
    run_cli("get_reverse_tracking_info")


if __name__ == "__main__":
    main()
