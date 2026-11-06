#!/usr/bin/env python3
"""
Amazon Store — Search Definitions Product Types (SP-API Product Type Definitions v2020-09-01)
===============================================================================================

通过 LinkFox **POST /spApi/developerProxy** 转发 **GET searchDefinitionsProductTypes**，
按关键词或商品标题搜索可用的 Amazon product type。

官方参考: https://developer-docs.amazon.com/sp-api/reference/searchdefinitionsproducttypes

Usage:
  python search_definitions_product_types.py '{
    "sellerId": "A1BCDEFGHIJK2",
    "region": "NA",
    "marketplaceIds": ["ATVPDKIKX0DER"],
    "keywords": ["luggage", "suitcase"]
  }'

或使用 itemName（与 keywords 互斥）:
  "itemName": "Carry-On Spinner 20 Inch"

Optional JSON:
  locale, searchLocale, skipDepCheck
"""

from typing import List

import json
import sys
from urllib.parse import quote

from _spapi_listings_common import ensure_auth_skill_available, run_proxy

DEFINITIONS_API_VERSION = "2020-09-01"
SEARCH_PATH = f"definitions/{DEFINITIONS_API_VERSION}/productTypes"


def _norm_marketplace_ids(val: object) -> List[str]:
    if isinstance(val, str):
        return [x.strip() for x in val.split(",") if x.strip()]
    if isinstance(val, list):
        return [str(x).strip() for x in val if str(x).strip()]
    raise ValueError("marketplaceIds must be a string or non-empty array")


def _keywords_nonempty(params: dict) -> bool:
    kw = params.get("keywords")
    if kw is None:
        return False
    if isinstance(kw, str):
        return bool(kw.strip())
    if isinstance(kw, list):
        return any(str(x).strip() for x in kw)
    return False


def _item_name_nonempty(params: dict) -> bool:
    n = params.get("itemName")
    return n is not None and str(n).strip() != ""


def _build_query(params: dict) -> str:
    mids = _norm_marketplace_ids(params["marketplaceIds"])
    if not mids:
        raise ValueError("marketplaceIds is required")
    parts: List[str] = [f"marketplaceIds={quote(','.join(mids), safe='')}"]

    has_kw = _keywords_nonempty(params)
    has_in = _item_name_nonempty(params)
    if has_kw and has_in:
        raise ValueError("keywords and itemName cannot be used together (Amazon API)")

    kw = params.get("keywords")
    if has_kw:
        if isinstance(kw, list):
            kstr = ",".join(str(x).strip() for x in kw if str(x).strip())
        else:
            kstr = str(kw).strip()
        if kstr:
            parts.append(f"keywords={quote(kstr, safe='')}")

    if has_in:
        parts.append(f"itemName={quote(str(params['itemName']).strip(), safe='')}")

    loc = params.get("locale")
    if loc is not None and str(loc).strip():
        parts.append(f"locale={quote(str(loc).strip(), safe='')}")

    sl = params.get("searchLocale")
    if sl is not None and str(sl).strip():
        parts.append(f"searchLocale={quote(str(sl).strip(), safe='')}")

    return "&".join(parts)


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: search_definitions_product_types.py '<JSON>'\n"
            "Required: sellerId, region, marketplaceIds\n"
            "Optional: keywords (array or string, comma-separated) OR itemName — not both\n"
            "Optional: locale, searchLocale\n"
            "See https://developer-docs.amazon.com/sp-api/reference/searchdefinitionsproducttypes",
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

    for f in ("sellerId", "region", "marketplaceIds"):
        if f not in params:
            print(f"Missing required field: {f}", file=sys.stderr)
            sys.exit(1)

    seller_id = str(params["sellerId"])
    region = str(params["region"])

    try:
        query_string = _build_query(params)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    run_proxy("searchDefinitionsProductTypes", "GET", region, SEARCH_PATH, seller_id, query_string,
              result_field="productTypesSearchResult")


if __name__ == "__main__":
    main()
