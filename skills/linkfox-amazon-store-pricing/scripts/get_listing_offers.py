#!/usr/bin/env python3
"""
Amazon Store — getListingOffers (SP-API Product Pricing v0)
===========================================================

通过 LinkFox 店铺网关 **POST /spApi/developerProxy** 转发 **GET getListingOffers**，
返回**单个**卖家 SKU 在指定站点、指定成色下的最低报价类信息（以 Amazon 响应为准）。

官方参考: https://developer-docs.amazon.com/sp-api/reference/getlistingoffers

Usage:
  python get_listing_offers.py '{
    "sellerId": "A1BCDEFGHIJK2",
    "region": "NA",
    "sku": "My-Seller-SKU-001",
    "marketplaceId": "ATVPDKIKX0DER",
    "itemCondition": "New"
  }'

Optional JSON fields:
  - customerType: Consumer | Business
  - marketplaceIds: 若提供数组则仅取第一个作为 MarketplaceId
  - skipDepCheck: boolean
"""

from __future__ import annotations

from typing import Optional

import json
import sys
from urllib.parse import quote

from _spapi_pricing_common import run_proxy, ensure_auth_skill_available

LISTING_OFFERS_PREFIX = "products/pricing/v0/listings"

def _path_for_listing_offers(sku: str) -> str:
    enc_sku = quote(sku, safe="")
    return f"{LISTING_OFFERS_PREFIX}/{enc_sku}/offers"


def _build_query_string(
    marketplace_id: str,
    item_condition: str,
    customer_type: Optional[str],
) -> str:
    parts: list[str] = [
        f"MarketplaceId={quote(marketplace_id, safe='')}",
        f"ItemCondition={quote(item_condition.strip(), safe='')}",
    ]
    if customer_type:
        parts.append(f"CustomerType={quote(customer_type.strip(), safe='')}")
    return "&".join(parts)


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: get_listing_offers.py '<JSON>'\n"
            "Required: sellerId, region, sku (seller SKU), marketplaceId (or marketplaceIds[0]), "
            "itemCondition (New|Used|Collectible|Refurbished|Club).\n"
            "Example: get_listing_offers.py "
            '\'{"sellerId":"A1...","region":"NA","sku":"MY-SKU","marketplaceId":"ATVPDKIKX0DER",'
            '"itemCondition":"New"}\'',
            file=sys.stderr,
        )
        sys.exit(1)
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available()

    for f in ("sellerId", "region", "sku", "itemCondition"):
        if f not in params:
            print(f"Missing required field: {f}", file=sys.stderr)
            sys.exit(1)

    mid = params.get("marketplaceId")
    if mid is None and params.get("marketplaceIds") is not None:
        mids = params["marketplaceIds"]
        if isinstance(mids, list) and mids:
            mid = mids[0]
            if len(mids) > 1:
                print(
                    "⚠️  Warning: getListingOffers expects a single MarketplaceId; "
                    "using first marketplaceIds only.",
                    file=sys.stderr,
                )
        elif isinstance(mids, str) and mids.strip():
            mid = mids.strip()
    if mid is None or (isinstance(mid, str) and not mid.strip()):
        print("Missing marketplaceId (or non-empty marketplaceIds)", file=sys.stderr)
        sys.exit(1)
    marketplace_id = str(mid).strip()

    seller_id = str(params["sellerId"])
    region = str(params["region"])
    sku = str(params["sku"])
    if not sku.strip():
        print("sku must be non-empty", file=sys.stderr)
        sys.exit(1)

    item_condition = str(params["itemCondition"])
    customer_type = params.get("customerType")
    if customer_type is not None:
        customer_type = str(customer_type)

    query_string = _build_query_string(marketplace_id, item_condition, customer_type)
    path = _path_for_listing_offers(sku)

    run_proxy("getListingOffers", "GET", region, path, seller_id, query_string,
              result_field="listingOffers")


if __name__ == "__main__":
    main()
