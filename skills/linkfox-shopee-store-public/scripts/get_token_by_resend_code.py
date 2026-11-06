#!/usr/bin/env python3
"""使用 resend code 获取 token；入参见 references/apis/get-token-by-resend-code.md。"""

from _public_api_runner import invoke_public_cli


def main() -> None:
    invoke_public_cli("get_token_by_resend_code")


if __name__ == "__main__":
    main()
