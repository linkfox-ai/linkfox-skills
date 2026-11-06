#!/usr/bin/env python3
"""刷新 access token；入参见 references/apis/refresh-access-token.md。"""

from _public_api_runner import invoke_public_cli


def main() -> None:
    invoke_public_cli("refresh_access_token")


if __name__ == "__main__":
    main()
