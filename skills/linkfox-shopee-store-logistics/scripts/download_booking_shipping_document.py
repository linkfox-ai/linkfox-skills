#!/usr/bin/env python3
"""
Shopee Store — download_booking_shipping_document

官方: https://open.shopee.com/documents/v2/v2.logistics.download_booking_shipping_document?module=95&type=1

入参说明见 references/apis/download-booking-shipping-document.md。
"""

from __future__ import annotations

import json
import sys

from _logistics_api_runner import run_logistics_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: download_booking_shipping_document.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    run_logistics_api("download_booking_shipping_document", params, "download_booking_shipping_document.py")


if __name__ == "__main__":
    main()
