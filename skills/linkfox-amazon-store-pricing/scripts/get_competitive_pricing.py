#!/usr/bin/env python3
"""
Amazon Store — getCompetitivePricing (SP-API Product Pricing v0)
================================================================

通过 LinkFox 店铺网关 **POST /spApi/developerProxy** 转发 **GET getCompetitivePricing**，
与 `get_pricing.py` 使用同一套代理接口。

官方参考: https://developer-docs.amazon.com/sp-api/reference/getcompetitivepricing

Usage:
  python get_competitive_pricing.py '{
    "sellerId": "A1BCDEFGHIJK2",
    "region": "NA",
    "marketplaceId": "ATVPDKIKX0DER",
    "itemType": "Asin",
    "asins": ["B08N5WRWNW"]
  }'

Optional JSON fields:
  - customerType: Consumer | Business（默认 Consumer，不传则由上游决定）
  - marketplaceIds: 若提供数组则仅取第一个作为 MarketplaceId
  - skipDepCheck: boolean
"""

from __future__ import annotations

from typing import List, Optional

import json
import sys
from urllib.parse import quote

from _spapi_pricing_common import run_proxy, ensure_auth_skill_available

COMPETITIVE_PRICE_PATH = "products/pricing/v0/competitivePrice"
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
    customer_type: Optional[str],
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
    if customer_type:
        parts.append(f"CustomerType={quote(customer_type.strip(), safe='')}")
    return "&".join(parts)


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: get_competitive_pricing.py '<JSON>'\n"
            "Required: sellerId, region, marketplaceId (or marketplaceIds[0]), "
            'itemType ("Asin"|"Sku"), and asins[] or skus[] (1..20 ids).\n'
            "Example: get_competitive_pricing.py "
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
                    "⚠️  Warning: getCompetitivePricing expects a single MarketplaceId; "
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
    item_type = str(params["itemType"]).strip()

    asins = _normalize_id_list(params.get("asins"), "asins")
    skus = _normalize_id_list(params.get("skus"), "skus")

    if item_type == "Asin":
        ids = asins
        if skus:
            print(
                "When itemType is Asin, do not pass skus (prefer asins only).",
                file=sys.stderr,
            )
    elif item_type == "Sku":
        ids = skus
        if asins:
            print(
                "When itemType is Sku, do not pass asins (prefer skus only).",
                file=sys.stderr,
            )
    else:
        ids = []

    if not ids:
        print("Provide non-empty asins (for ItemType Asin) or skus (for ItemType Sku).", file=sys.stderr)
        sys.exit(1)
    if len(ids) > MAX_IDENTIFIERS:
        print(f"At most {MAX_IDENTIFIERS} Asins or Skus per request.", file=sys.stderr)
        sys.exit(1)

    customer_type = params.get("customerType")
    if customer_type is not None:
        customer_type = str(customer_type)

    try:
        query_string = _build_query_string(
            marketplace_id,
            item_type,
            asins if item_type == "Asin" else [],
            skus if item_type == "Sku" else [],
            customer_type,
        )
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    path = COMPETITIVE_PRICE_PATH

    run_proxy("getCompetitivePricing", "GET", region, path, seller_id, query_string,
              result_field="competitivePricing")


if __name__ == "__main__":
    main()
