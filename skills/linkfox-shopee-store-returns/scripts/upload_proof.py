#!/usr/bin/env python3
"""Shopee 店铺 — 上传退货凭证（upload_proof）。

官方：https://open.shopee.com/documents/v2/v2.returns.upload_proof?module=102&type=1
入参与响应见 references/apis/upload-proof.md。
"""

from _returns_api_runner import run_cli


def main() -> None:
    run_cli("upload_proof")


if __name__ == "__main__":
    main()
