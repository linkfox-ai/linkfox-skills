#!/usr/bin/env python3
"""查询 Shopee 开放平台 IP 段；入参见 references/apis/get-shopee-ip-ranges.md。"""

from _public_api_runner import invoke_public_cli


def main() -> None:
    invoke_public_cli("get_shopee_ip_ranges")


if __name__ == "__main__":
    main()
