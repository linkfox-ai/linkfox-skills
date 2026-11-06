#!/usr/bin/env python3
"""Shopee 店铺 — 上传退货运单凭证（upload_shipping_proof）。

官方：https://open.shopee.com/documents/v2/v2.returns.upload_shipping_proof?module=102&type=1
入参与响应见 references/apis/upload-shipping-proof.md。
"""

from _returns_api_runner import run_cli


def main() -> None:
    run_cli("upload_shipping_proof")


if __name__ == "__main__":
    main()
