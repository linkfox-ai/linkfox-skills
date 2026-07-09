#!/usr/bin/env python3
"""
Amazon Store — listCatalogCategories (SP-API Catalog Items v0)
==============================================================

GET `catalog/v0/categories`。须传 **MarketplaceId** 以及 **ASIN** 或 **SellerSKU** 之一。

官方参考: https://developer-docs.amazon.com/sp-api/reference/listcatalogcategories
"""

from __future__ import annotations

import json
import sys
from urllib.parse import quote

from _spapi_catalog_common import (
    developer_proxy_get,
    emit_result,
    ensure_auth_skill_available,
    get_store_tokens,
    lf_inline_flag,
    load_cli_params,
    merge_success_json,
    norm_marketplace_ids,
    require_seller_region,
)

PATH = "catalog/v0/categories"


def _build_query(params: dict) -> str:
    mids = norm_marketplace_ids(params, max_count=1)
    if not mids:
        print("Missing marketplaceId or marketplaceIds (use one id)", file=sys.stderr)
        sys.exit(1)
    if len(mids) > 1:
        print("listCatalogCategories uses a single MarketplaceId; using first only.", file=sys.stderr)

    asin = params.get("asin") or params.get("ASIN")
    sku = params.get("sellerSku") or params.get("SellerSKU")
    if asin and sku:
        print("Provide only one of asin/ASIN or sellerSku/SellerSKU.", file=sys.stderr)
        sys.exit(1)
    if not asin and not sku:
        print("Required: asin (or ASIN) OR sellerSku (or SellerSKU).", file=sys.stderr)
        sys.exit(1)

    parts = [f"MarketplaceId={quote(mids[0], safe='')}"]
    if asin:
        parts.append(f"ASIN={quote(str(asin).strip(), safe='')}")
    else:
        parts.append(f"SellerSKU={quote(str(sku).strip(), safe='')}")
    return "&".join(parts)


def main() -> None:
    params = load_cli_params()
    if not params:
        print(
            "Usage: list_catalog_categories.py '<JSON>'\n"
            "Required: sellerId, region, marketplaceId(s), and asin OR sellerSku",
            file=sys.stderr,
        )
        sys.exit(1)

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available("list_catalog_categories.py")

    seller_id, region = require_seller_region(params)
    qs = _build_query(params)

    tokens = get_store_tokens(seller_id, region)
    if "error" in tokens or "accessToken" not in tokens:
        print(json.dumps(tokens, indent=2, ensure_ascii=False))
        sys.exit(1)

    proxy = developer_proxy_get(region, PATH, tokens["accessToken"], query_string=qs)
    out: dict = {"developerProxy": proxy, "resolvedPath": PATH, "queryString": qs}
    merge_success_json(out, proxy, "categories")
    inline = lf_inline_flag()
    emit_result(out, inline)


if __name__ == "__main__":
    main()
