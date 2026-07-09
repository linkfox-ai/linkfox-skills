#!/usr/bin/env python3
"""
Amazon Store — getItemOffers (SP-API Product Pricing v0)
=========================================================

GET 单个 ASIN 在指定站点、成色下的低价报价类信息（以 Amazon 响应为准）。

官方参考: https://developer-docs.amazon.com/sp-api/reference/getitemoffers

Usage:
  python get_item_offers.py '{
    "sellerId": "A1BCDEFGHIJK2",
    "region": "NA",
    "asin": "B08N5WRWNW",
    "marketplaceId": "ATVPDKIKX0DER",
    "itemCondition": "New"
  }'

Optional: customerType (Consumer|Business), marketplaceIds, skipDepCheck
"""

from __future__ import annotations

import json
import sys
from typing import Optional

from urllib.parse import quote

from _spapi_pricing_common import (
    developer_proxy_get,
    emit_result,
    ensure_auth_skill_available,
    get_store_tokens,
    lf_inline_flag,
    resolve_marketplace_id,
)


def _path(asin: str) -> str:
    return f"products/pricing/v0/items/{quote(asin.strip(), safe='')}/offers"


def _query(mid: str, item_condition: str, customer_type: Optional[str]) -> str:
    parts = [
        f"MarketplaceId={quote(mid, safe='')}",
        f"ItemCondition={quote(item_condition.strip(), safe='')}",
    ]
    if customer_type:
        parts.append(f"CustomerType={quote(customer_type.strip(), safe='')}")
    return "&".join(parts)


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: get_item_offers.py '<JSON>'\n"
            "Required: sellerId, region, asin, marketplaceId (or marketplaceIds[0]), "
            "itemCondition.\n"
            'Example: get_item_offers.py '
            '\'{"sellerId":"A1...","region":"NA","asin":"B0...","marketplaceId":"ATVPDKIKX0DER",'
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
        ensure_auth_skill_available("get_item_offers.py")

    for f in ("sellerId", "region", "asin", "itemCondition"):
        if f not in params:
            print(f"Missing required field: {f}", file=sys.stderr)
            sys.exit(1)

    try:
        marketplace_id = resolve_marketplace_id(params, "getItemOffers")
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    asin = str(params["asin"]).strip()
    if not asin:
        print("asin must be non-empty", file=sys.stderr)
        sys.exit(1)

    seller_id = str(params["sellerId"])
    region = str(params["region"])
    item_condition = str(params["itemCondition"])
    ct = params.get("customerType")
    if ct is not None:
        ct = str(ct)

    path = _path(asin)
    q = _query(marketplace_id, item_condition, ct)

    tokens = get_store_tokens(seller_id, region)
    if "error" in tokens or "accessToken" not in tokens:
        print(json.dumps(tokens, indent=2, ensure_ascii=False))
        sys.exit(1)

    proxy = developer_proxy_get(region, path, tokens["accessToken"], q)
    out: dict = {"developerProxy": proxy, "resolvedPath": path, "queryString": q}
    if proxy.get("errcode") == 200 and proxy.get("httpStatus") == 200:
        raw = proxy.get("body") or "{}"
        try:
            out["itemOffers"] = json.loads(raw)
        except json.JSONDecodeError:
            out["itemOffers"] = None
            out["itemOffersRaw"] = raw
    emit_result(out, lf_inline_flag())


if __name__ == "__main__":
    main()
