#!/usr/bin/env python3
"""
Shopee Store — create_booking_shipping_document

官方: https://open.shopee.com/documents/v2/v2.logistics.create_booking_shipping_document?module=95&type=1

入参说明见 references/apis/create-booking-shipping-document.md。
"""

from __future__ import annotations

import json
import sys

from _logistics_api_runner import run_logistics_api


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: create_booking_shipping_document.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    run_logistics_api("create_booking_shipping_document", params, "create_booking_shipping_document.py")


if __name__ == "__main__":
    main()
