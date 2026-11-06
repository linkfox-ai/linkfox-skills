#!/usr/bin/env python3
"""Shopee 店铺 — 查询退货凭证（query_proof）。

官方：https://open.shopee.com/documents/v2/v2.returns.query_proof?module=102&type=1
入参与响应见 references/apis/query-proof.md。
"""

from _returns_api_runner import run_cli


def main() -> None:
    run_cli("query_proof")


if __name__ == "__main__":
    main()
