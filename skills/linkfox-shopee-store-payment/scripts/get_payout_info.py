#!/usr/bin/env python3
"""
Shopee Store — get_payout_info

官方: https://open.shopee.com/documents/v2/v2.payment.get_payout_info?module=97&type=1

入参说明见 references/apis/get-payout-info.md。
"""

from __future__ import annotations

import json

from _payment_api_runner import main_for_api


def main() -> None:
    main_for_api("get_payout_info")


if __name__ == "__main__":
    main()
