#!/usr/bin/env python3
"""Shopee 套装优惠操作：delete_bundle_deal。参数说明见 references/apis/delete-bundle-deal.md。"""

from __future__ import annotations

from _bundle_deal_api_runner import script_main


def main() -> None:
    script_main('delete_bundle_deal')


if __name__ == "__main__":
    main()
