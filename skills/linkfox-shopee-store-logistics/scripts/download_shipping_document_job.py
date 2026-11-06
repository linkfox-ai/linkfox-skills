#!/usr/bin/env python3
"""
Shopee Store — download_shipping_document_job

官方: https://open.shopee.com/documents/v2/v2.logistics.download_shipping_document_job?module=95&type=1

入参说明见 references/apis/download-shipping-document-job.md。
"""

from __future__ import annotations

import json
import sys

from _logistics_api_runner import run_logistics_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: download_shipping_document_job.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    run_logistics_api("download_shipping_document_job", params, "download_shipping_document_job.py")


if __name__ == "__main__":
    main()
