#!/usr/bin/env python3
"""
Amazon Store — searchCatalogItems (SP-API Catalog Items v2022-04-01 默认)
==========================================================================

GET `catalog/{version}/items`。默认 **2022-04-01**；可设 `catalogItemsVersion` 为 **2020-12-01**。

须 **marketplaceIds**（文档通常 ≤1），且 **keywords** 与 **identifiers+identifiersType** 二选一。

官方参考: https://developer-docs.amazon.com/sp-api/reference/searchcatalogitems
"""

from __future__ import annotations

import sys
from urllib.parse import quote

from _spapi_catalog_common import (
    CATALOG_ITEMS_V2020,
    CATALOG_ITEMS_V2022,
    catalog_items_path,
    run_proxy,
    ensure_auth_skill_available,
    load_cli_params,
    norm_marketplace_ids,
    require_seller_region,
    resolve_catalog_items_version,
    str_list,
)

IDENTIFIERS_TYPE_ENUM = frozenset(
    {"ASIN", "EAN", "GTIN", "ISBN", "JAN", "MINSAN", "SKU", "UPC"}
)


def _build_query(params: dict) -> str:
    mids = norm_marketplace_ids(params, max_count=1)
    if not mids:
        print("Missing marketplaceIds (or marketplaceId).", file=sys.stderr)
        sys.exit(1)

    keywords = str_list(params.get("keywords"), "keywords")
    identifiers = str_list(params.get("identifiers"), "identifiers")
    id_type = str(params.get("identifiersType") or "").strip().upper()

    if keywords and identifiers:
        print("keywords and identifiers cannot be used together.", file=sys.stderr)
        sys.exit(1)
    if not keywords and not identifiers:
        print("Required: keywords OR (identifiers + identifiersType).", file=sys.stderr)
        sys.exit(1)
    if identifiers and not id_type:
        print("identifiersType is required when identifiers is set.", file=sys.stderr)
        sys.exit(1)
    if id_type and str(id_type).strip().upper() not in IDENTIFIERS_TYPE_ENUM:
        print(f"identifiersType must be one of: {sorted(IDENTIFIERS_TYPE_ENUM)}", file=sys.stderr)
        sys.exit(1)
    if len(keywords) > 20:
        print("keywords length must be ≤ 20", file=sys.stderr)
        sys.exit(1)
    if len(identifiers) > 20:
        print("identifiers length must be ≤ 20", file=sys.stderr)
        sys.exit(1)

    parts: list[str] = []

    def add(k: str, v: str) -> None:
        parts.append(f"{k}={quote(v, safe='')}")

    for mid in mids:
        add("marketplaceIds", mid)
    for kw in keywords:
        add("keywords", kw)
    for ident in identifiers:
        add("identifiers", ident)
    if id_type:
        add("identifiersType", str(id_type).strip())
    for inc in str_list(params.get("includedData"), "includedData"):
        add("includedData", inc)
    for bn in str_list(params.get("brandNames"), "brandNames"):
        add("brandNames", bn)
    for cid in str_list(params.get("classificationIds"), "classificationIds"):
        add("classificationIds", cid)

    if params.get("locale"):
        add("locale", str(params["locale"]).strip())
    if params.get("keywordsLocale"):
        add("keywordsLocale", str(params["keywordsLocale"]).strip())
    if params.get("sellerIdForCatalog"):
        add("sellerId", str(params["sellerIdForCatalog"]).strip())
    elif id_type == "SKU":
        sid = params.get("sellerId")
        if sid:
            add("sellerId", str(sid).strip())

    if params.get("pageSize") is not None:
        try:
            raw_page_size = params["pageSize"]
            ps = int(raw_page_size)
            if isinstance(raw_page_size, bool) or (
                isinstance(raw_page_size, float) and raw_page_size != ps
            ):
                raise ValueError("pageSize 不能是布尔值或小数。")
        except (TypeError, ValueError, OverflowError):
            print("pageSize 必须为 1～20 的整数。", file=sys.stderr)
            raise SystemExit(1)
        if ps < 1 or ps > 20:
            print("pageSize must be between 1 and 20", file=sys.stderr)
            sys.exit(1)
        add("pageSize", str(ps))
    if params.get("pageToken"):
        add("pageToken", str(params["pageToken"]).strip())

    return "&".join(parts)


def main() -> None:
    params = load_cli_params()
    if not params:
        print(
            "Usage: search_catalog_items.py '<JSON>'\n"
            "Required: sellerId, region, marketplaceIds, and keywords OR identifiers+identifiersType\n"
            "Optional: includedData, brandNames, classificationIds, locale, pageSize, pageToken, "
            f"catalogItemsVersion ({CATALOG_ITEMS_V2022}|{CATALOG_ITEMS_V2020})",
            file=sys.stderr,
        )
        sys.exit(1)

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available("search_catalog_items.py")

    seller_id, region = require_seller_region(params)
    version = resolve_catalog_items_version(params)
    path = catalog_items_path(version)
    qs = _build_query(params)

    run_proxy(
        "searchCatalogItems", region, path, seller_id, qs,
        result_key="catalogItems", version=version,
    )


if __name__ == "__main__":
    main()
