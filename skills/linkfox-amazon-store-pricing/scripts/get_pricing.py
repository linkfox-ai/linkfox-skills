#!/usr/bin/env python3
"""
Amazon Store — getPricing (SP-API Product Pricing v0)
======================================================

通过 LinkFox 店铺网关 **POST /spApi/developerProxy** 转发 **GET getPricing**，
与 `linkfox-amazon-store-report` / `linkfox-amazon-store-listings` 使用同一套代理接口。

官方参考: https://developer-docs.amazon.com/sp-api/reference/getpricing

Usage:
  python get_pricing.py '{
    "sellerId": "A1BCDEFGHIJK2",
    "region": "NA",
    "marketplaceId": "ATVPDKIKX0DER",
    "itemType": "Asin",
    "asins": ["B08N5WRWNW"]
  }'

  # 按 SKU（最多 20 个）
  python get_pricing.py '{"sellerId":"...","region":"NA","marketplaceId":"ATVPDKIKX0DER","itemType":"Sku","skus":["MY-SKU-1"]}'

Optional JSON fields:
  - itemCondition: New | Used | Collectible | Refurbished | Club
  - offerType: B2C | B2B（默认 B2C，不传则由上游决定）
  - marketplaceIds: 若提供数组则仅取第一个作为 MarketplaceId（与 listing 系列脚本习惯一致）
  - skipDepCheck: boolean
"""

from __future__ import annotations

from typing import List, Optional

import json
import sys
from urllib.parse import quote

from _spapi_pricing_common import run_proxy, ensure_auth_skill_available

PRICING_PATH = "products/pricing/v0/price"
MAX_IDENTIFIERS = 20

def _normalize_id_list(raw: object, field_name: str) -> List[str]:
    if raw is None:
        return []
    if isinstance(raw, str):
        s = raw.strip()
        return [s] if s else []
    if isinstance(raw, list):
        return [str(x).strip() for x in raw if str(x).strip()]
    print(f"{field_name} must be a string or array of strings", file=sys.stderr)
    sys.exit(1)


def _build_query_string(
    marketplace_id: str,
    item_type: str,
    asins: List[str],
    skus: List[str],
    item_condition: Optional[str],
    offer_type: Optional[str],
) -> str:
    parts: list[str] = [
        f"MarketplaceId={quote(marketplace_id, safe='')}",
        f"ItemType={quote(item_type, safe='')}",
    ]
    it = item_type.strip()
    if it == "Asin":
        for a in asins[:MAX_IDENTIFIERS]:
            parts.append(f"Asins={quote(a, safe='')}")
    elif it == "Sku":
        for s in skus[:MAX_IDENTIFIERS]:
            parts.append(f"Skus={quote(s, safe='')}")
    else:
        raise ValueError('itemType must be "Asin" or "Sku" (case-sensitive per Amazon)')
    if item_condition:
        parts.append(f"ItemCondition={quote(item_condition.strip(), safe='')}")
    if offer_type:
        parts.append(f"OfferType={quote(offer_type.strip(), safe='')}")
    return "&".join(parts)


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: get_pricing.py '<JSON>'\n"
            "Required: sellerId, region, marketplaceId (or marketplaceIds[0]), "
            'itemType ("Asin"|"Sku"), and asins[] or skus[] (1..20 ids).\n'
            "Example: get_pricing.py "
            '\'{"sellerId":"A1...","region":"NA","marketplaceId":"ATVPDKIKX0DER",'
            '"itemType":"Asin","asins":["B0XXXXXXXX"]}\'',
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

    for f in ("sellerId", "region", "itemType"):
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
                    "⚠️  Warning: getPricing expects a single MarketplaceId; using first marketplaceIds only.",
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
    item_type = str(params["itemType"]).strip()

    asins = _normalize_id_list(params.get("asins"), "asins")
    skus = _normalize_id_list(params.get("skus"), "skus")

    if item_type == "Asin":
        ids = asins
        if skus:
            print("When itemType is Asin, do not pass skus (ignored if both set; prefer asins only).", file=sys.stderr)
    elif item_type == "Sku":
        ids = skus
        if asins:
            print("When itemType is Sku, do not pass asins (ignored if both set; prefer skus only).", file=sys.stderr)
    else:
        ids = []

    if not ids:
        print("Provide non-empty asins (for ItemType Asin) or skus (for ItemType Sku).", file=sys.stderr)
        sys.exit(1)
    if len(ids) > MAX_IDENTIFIERS:
        print(f"At most {MAX_IDENTIFIERS} Asins or Skus per request.", file=sys.stderr)
        sys.exit(1)

    item_condition = params.get("itemCondition")
    if item_condition is not None:
        item_condition = str(item_condition)
    offer_type = params.get("offerType")
    if offer_type is not None:
        offer_type = str(offer_type)

    try:
        query_string = _build_query_string(
            marketplace_id,
            item_type,
            asins if item_type == "Asin" else [],
            skus if item_type == "Sku" else [],
            item_condition,
            offer_type,
        )
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    path = PRICING_PATH

    run_proxy("getPricing", "GET", region, path, seller_id, query_string,
              result_field="pricing")


if __name__ == "__main__":
    main()
