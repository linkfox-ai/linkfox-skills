#!/usr/bin/env python3
"""
Amazon Store — listCatalogCategories (SP-API Catalog Items v0)
==============================================================

GET `catalog/v0/categories`。须传 **MarketplaceId** 以及 **ASIN** 或 **SellerSKU** 之一。

官方参考: https://developer-docs.amazon.com/sp-api/reference/listcatalogcategories
"""

from __future__ import annotations

import sys
from urllib.parse import quote

from _spapi_catalog_common import (
    run_proxy,
    ensure_auth_skill_available,
    load_cli_params,
    norm_marketplace_ids,
    require_seller_region,
)

PATH = "catalog/v0/categories"


def _build_query(params: dict) -> str:
    mids = norm_marketplace_ids(params, max_count=1)
    if not mids:
        print("Missing marketplaceId or marketplaceIds (use one id)", file=sys.stderr)
        sys.exit(1)
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

    run_proxy(
        "listCatalogCategories", region, PATH, seller_id, qs,
        result_key="categories",
    )


if __name__ == "__main__":
    main()
