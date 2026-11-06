#!/usr/bin/env python3
"""
Shopee Store — generic Payment API caller
==========================================

Usage:
  python payment_api.py '{"api": "get_escrow_detail", "shopId": "67890", "order_sn": "240101ABC"}'

Official docs: https://open.shopee.com/documents/v2/v2.payment.<api>?module=97&type=1
"""

from __future__ import annotations

import json

from _payment_api_runner import main_for_api


def main() -> None:
    main_for_api()


if __name__ == "__main__":
    main()
