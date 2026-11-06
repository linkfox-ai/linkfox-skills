#!/usr/bin/env python3
"""Shopee 套装优惠操作：get_bundle_deal_item。参数说明见 references/apis/get-bundle-deal-item.md。"""

from __future__ import annotations

from _bundle_deal_api_runner import script_main


def main() -> None:
    script_main('get_bundle_deal_item')


if __name__ == "__main__":
    main()
