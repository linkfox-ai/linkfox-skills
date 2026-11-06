#!/usr/bin/env python3
"""
Amazon Store — Get Listings Restrictions (SP-API Listings Restrictions v2021-08-01)
==================================================================================

通过 LinkFox **POST /spApi/developerProxy** 转发 **GET getListingsRestrictions**，
查询目录 ASIN 在指定卖家与市场下的刊登限制。

官方参考: https://developer-docs.amazon.com/sp-api/reference/getlistingsrestrictions

Usage:
  python get_listings_restrictions.py '{
    "sellerId": "A1BCDEFGHIJK2",
    "region": "NA",
    "asin": "B08N5WRWNW",
    "marketplaceIds": ["ATVPDKIKX0DER"]
  }'

Optional JSON:
  conditionType (enum, 如 new / used_like_new 等), reasonLocale, skipDepCheck
"""

from typing import List

import json
import sys
from urllib.parse import quote

from _spapi_listings_common import ensure_auth_skill_available, run_proxy

LISTINGS_API_VERSION = "2021-08-01"
RESTRICTIONS_PATH = f"listings/{LISTINGS_API_VERSION}/restrictions"


def _norm_marketplace_ids(val: object) -> List[str]:
    if isinstance(val, str):
        return [x.strip() for x in val.split(",") if x.strip()]
    if isinstance(val, list):
        return [str(x).strip() for x in val if str(x).strip()]
    raise ValueError("marketplaceIds must be a string or non-empty array")


def _build_query(params: dict, seller_id: str, asin: str) -> str:
    mids = _norm_marketplace_ids(params["marketplaceIds"])
    if not mids:
        raise ValueError("marketplaceIds is required")
    parts: List[str] = [
        f"asin={quote(asin, safe='')}",
        f"sellerId={quote(seller_id, safe='')}",
        f"marketplaceIds={quote(','.join(mids), safe='')}",
    ]
    ct = params.get("conditionType")
    if ct is not None and str(ct).strip():
        parts.append(f"conditionType={quote(str(ct).strip(), safe='')}")
    rl = params.get("reasonLocale")
    if rl is not None and str(rl).strip():
        parts.append(f"reasonLocale={quote(str(rl).strip(), safe='')}")
    return "&".join(parts)


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: get_listings_restrictions.py '<JSON>'\n"
            "Required: sellerId, region, asin, marketplaceIds\n"
            "Optional: conditionType, reasonLocale\n"
            "See https://developer-docs.amazon.com/sp-api/reference/getlistingsrestrictions",
            file=sys.stderr,
        )
        sys.exit(1)
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(params, dict):
        print("JSON parameters must be an object", file=sys.stderr)
        sys.exit(1)

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available()

    for f in ("sellerId", "region", "asin", "marketplaceIds"):
        if f not in params:
            print(f"Missing required field: {f}", file=sys.stderr)
            sys.exit(1)

    seller_id = str(params["sellerId"])
    region = str(params["region"])
    asin = str(params["asin"]).strip()
    if not asin:
        print("asin must be non-empty", file=sys.stderr)
        sys.exit(1)

    try:
        query_string = _build_query(params, seller_id, asin)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    run_proxy("getListingsRestrictions", "GET", region, RESTRICTIONS_PATH, seller_id, query_string,
              result_field="restrictionsResult")


if __name__ == "__main__":
    main()
