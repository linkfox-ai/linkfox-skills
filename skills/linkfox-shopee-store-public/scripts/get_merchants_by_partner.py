#!/usr/bin/env python3
"""查询 Partner 下已授权商户；入参见 references/apis/get-merchants-by-partner.md。"""

from _public_api_runner import invoke_public_cli


def main() -> None:
    invoke_public_cli("get_merchants_by_partner")


if __name__ == "__main__":
    main()
