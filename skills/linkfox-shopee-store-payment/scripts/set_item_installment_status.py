#!/usr/bin/env python3
"""
Shopee Store — set_item_installment_status

官方: https://open.shopee.com/documents/v2/v2.payment.set_item_installment_status?module=97&type=1

入参说明见 references/apis/set-item-installment-status.md。
"""

from __future__ import annotations

import json

from _payment_api_runner import main_for_api


def main() -> None:
    main_for_api("set_item_installment_status")


if __name__ == "__main__":
    main()
