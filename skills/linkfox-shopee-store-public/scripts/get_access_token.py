#!/usr/bin/env python3
"""使用授权码交换 token；入参见 references/apis/get-access-token.md。"""

from _public_api_runner import invoke_public_cli


def main() -> None:
    invoke_public_cli("get_access_token")


if __name__ == "__main__":
    main()
