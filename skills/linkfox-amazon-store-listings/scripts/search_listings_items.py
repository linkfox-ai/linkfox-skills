#!/usr/bin/env python3
"""
Amazon Store — Search Listings Items (SP-API Listings Items v2021-08-01)
========================================================================

通过 LinkFox 店铺网关 **POST /spApi/developerProxy** 转发 **GET searchListingsItems**，
与 `get_listings_item.py` 使用同一套 **sellerId + region + developerProxy** 流程。

官方参考: https://developer-docs.amazon.com/sp-api/reference/searchlistingsitems

Usage:
  python search_listings_items.py '{
    "sellerId": "A1BCDEFGHIJK2",
    "region": "NA",
    "marketplaceIds": ["ATVPDKIKX0DER"]
  }'

Optional filters (见脚本内校验与 references/api.md):
  identifiers + identifiersType | variationParentSku | packageHierarchySku（三者互斥）
  issueLocale, includedData, 时间窗, withIssueSeverity, withStatus, withoutStatus,
  sortBy, sortOrder, pageSize (≤20, 默认 10), pageToken
  skipDepCheck: boolean
"""

from typing import List, Optional, Sequence

import json
import sys
from urllib.parse import quote

from _spapi_listings_common import ensure_auth_skill_available, run_proxy

LISTINGS_API_VERSION = "2021-08-01"


IDENTIFIERS_TYPE_ENUM = frozenset(
    {"SKU", "ASIN", "EAN", "FNSKU", "GTIN", "ISBN", "JAN", "MINSAN", "UPC"}
)


def _path_for_search_listings_items(seller_id: str) -> str:
    return f"listings/{LISTINGS_API_VERSION}/items/{quote(seller_id, safe='')}"


def _comma_param(key: str, values: Sequence[str]) -> str:
    return f"{key}={quote(','.join(values), safe='')}"


def _norm_str_list(val: object, field: str, max_n: Optional[int] = None) -> List[str]:
    if val is None:
        return []
    if isinstance(val, str):
        out = [x.strip() for x in val.split(",") if x.strip()]
    elif isinstance(val, list):
        out = [str(x).strip() for x in val if str(x).strip()]
    else:
        raise ValueError(f"{field} must be a string or array of strings")
    if max_n is not None and len(out) > max_n:
        raise ValueError(f"{field}: at most {max_n} values allowed (Amazon API)")
    return out


def build_search_query_string(params: dict) -> str:
    """Build queryString for searchListingsItems; validates mutual exclusion rules."""
    mids_raw = params.get("marketplaceIds")
    if isinstance(mids_raw, str):
        marketplace_ids = [mids_raw]
    elif isinstance(mids_raw, list):
        marketplace_ids = [str(x) for x in mids_raw]
    else:
        raise ValueError("marketplaceIds must be a string or non-empty array")
    if not marketplace_ids:
        raise ValueError("marketplaceIds is required")

    identifiers = _norm_str_list(params.get("identifiers"), "identifiers", max_n=20)
    identifiers_type = params.get("identifiersType")
    if isinstance(identifiers_type, str):
        identifiers_type = identifiers_type.strip() or None
    else:
        identifiers_type = None

    vps = params.get("variationParentSku")
    vps = str(vps).strip() if vps is not None and str(vps).strip() else None
    phs = params.get("packageHierarchySku")
    phs = str(phs).strip() if phs is not None and str(phs).strip() else None

    if vps and phs:
        raise ValueError("Cannot use both 'variationParentSku' and 'packageHierarchySku'")

    if identifiers and (vps or phs):
        raise ValueError(
            "Cannot use 'identifiers' together with 'variationParentSku' or 'packageHierarchySku'"
        )
    if vps and (identifiers or phs):
        raise ValueError("Cannot use 'variationParentSku' with 'identifiers' or 'packageHierarchySku'")
    if phs and (identifiers or vps):
        raise ValueError("Cannot use 'packageHierarchySku' with 'identifiers' or 'variationParentSku'")

    if identifiers and not identifiers_type:
        raise ValueError("identifiersType is required when 'identifiers' is provided")
    if identifiers_type and not identifiers:
        raise ValueError("identifiers is required when 'identifiersType' is provided")
    if identifiers_type and identifiers_type not in IDENTIFIERS_TYPE_ENUM:
        print(
            f"⚠️  Warning: identifiersType={identifiers_type!r} not in known enum "
            f"{sorted(IDENTIFIERS_TYPE_ENUM)}; sending anyway.",
            file=sys.stderr,
        )

    parts: List[str] = []
    mid = marketplace_ids[0]
    parts.append(f"marketplaceIds={quote(mid, safe='')}")
    if len(marketplace_ids) > 1:
        print(
            "⚠️  Warning: searchListingsItems marketplaceIds length ≤ 1; using first only.",
            file=sys.stderr,
        )

    inc = params.get("includedData")
    if inc is not None:
        if isinstance(inc, list):
            id_val = ",".join(str(x) for x in inc)
        else:
            id_val = str(inc).strip()
        if id_val:
            parts.append(f"includedData={quote(id_val, safe='')}")

    il = params.get("issueLocale")
    if il:
        parts.append(f"issueLocale={quote(str(il).strip(), safe='')}")

    if identifiers:
        parts.append(_comma_param("identifiers", identifiers))
        parts.append(f"identifiersType={quote(identifiers_type or '', safe='')}")
    if vps:
        parts.append(f"variationParentSku={quote(vps, safe='')}")
    if phs:
        parts.append(f"packageHierarchySku={quote(phs, safe='')}")

    for key in ("createdAfter", "createdBefore", "lastUpdatedAfter", "lastUpdatedBefore"):
        v = params.get(key)
        if v is not None and str(v).strip():
            parts.append(f"{key}={quote(str(v).strip(), safe='')}")

    wis = _norm_str_list(params.get("withIssueSeverity"), "withIssueSeverity")
    if wis:
        parts.append(_comma_param("withIssueSeverity", wis))
    ws = _norm_str_list(params.get("withStatus"), "withStatus")
    if ws:
        parts.append(_comma_param("withStatus", ws))
    wos = _norm_str_list(params.get("withoutStatus"), "withoutStatus")
    if wos:
        parts.append(_comma_param("withoutStatus", wos))

    sort_by = params.get("sortBy")
    if sort_by is not None and str(sort_by).strip():
        parts.append(f"sortBy={quote(str(sort_by).strip(), safe='')}")
    sort_order = params.get("sortOrder")
    if sort_order is not None and str(sort_order).strip():
        parts.append(f"sortOrder={quote(str(sort_order).strip(), safe='')}")

    page_size = params.get("pageSize", 10)
    try:
        ps = int(page_size)
    except (TypeError, ValueError):
        raise ValueError("pageSize must be an integer")
    if ps > 20:
        print("⚠️  Warning: pageSize capped to 20 (Amazon max).", file=sys.stderr)
        ps = 20
    if ps < 1:
        raise ValueError("pageSize must be >= 1")
    parts.append(f"pageSize={ps}")

    pt = params.get("pageToken")
    if pt is not None and str(pt).strip():
        parts.append(f"pageToken={quote(str(pt).strip(), safe='')}")

    return "&".join(parts)


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: search_listings_items.py '<JSON>'\n"
            "Required: sellerId, region, marketplaceIds\n"
            "Optional: identifiers+identifiersType | variationParentSku | packageHierarchySku (互斥), "
            "includedData, issueLocale, 时间过滤, withIssueSeverity, withStatus, withoutStatus, "
            "sortBy, sortOrder, pageSize (≤20), pageToken\n"
            "Example: search_listings_items.py "
            '\'{"sellerId":"A1...","region":"NA","marketplaceIds":["ATVPDKIKX0DER"],"pageSize":10}\'',
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
        query_string = build_search_query_string(params)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    path = _path_for_search_listings_items(seller_id)

    run_proxy("searchListingsItems", "GET", region, path, seller_id, query_string,
              result_field="searchResult")


if __name__ == "__main__":
    main()
