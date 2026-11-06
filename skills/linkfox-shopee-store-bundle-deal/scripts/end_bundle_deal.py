#!/usr/bin/env python3
"""Shopee 套装优惠操作：end_bundle_deal。参数说明见 references/apis/end-bundle-deal.md。"""

from __future__ import annotations

from _bundle_deal_api_runner import script_main


def main() -> None:
    script_main('end_bundle_deal')


if __name__ == "__main__":
    main()
