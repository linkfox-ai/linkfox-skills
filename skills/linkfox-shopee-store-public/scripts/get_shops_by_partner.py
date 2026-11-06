#!/usr/bin/env python3
"""查询 Partner 下已授权店铺；入参见 references/apis/get-shops-by-partner.md。"""

from _public_api_runner import invoke_public_cli


def main() -> None:
    invoke_public_cli("get_shops_by_partner")


if __name__ == "__main__":
    main()
