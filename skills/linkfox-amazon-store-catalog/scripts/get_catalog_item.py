#!/usr/bin/env python3
"""
Amazon Store — getCatalogItem (SP-API Catalog Items v2022-04-01 默认)
======================================================================

GET `catalog/{version}/items/{asin}`。默认 **2022-04-01**。

官方参考: https://developer-docs.amazon.com/sp-api/reference/getcatalogitem
"""

from __future__ import annotations

import json
import sys
from urllib.parse import quote

from _spapi_catalog_common import (
    CATALOG_ITEMS_V2020,
    CATALOG_ITEMS_V2022,
    catalog_items_path,
    developer_proxy_get,
    emit_result,
    encode_path_segment,
    ensure_auth_skill_available,
    get_store_tokens,
    lf_inline_flag,
    load_cli_params,
    merge_success_json,
    norm_marketplace_ids,
    require_seller_region,
    resolve_catalog_items_version,
    str_list,
)


def _build_query(params: dict) -> str:
    mids = norm_marketplace_ids(params, max_count=1)
    if not mids:
        print("Missing marketplaceIds (or marketplaceId).", file=sys.stderr)
        sys.exit(1)

    parts: list[str] = [f"marketplaceIds={quote(mids[0], safe='')}"]
    for inc in str_list(params.get("includedData"), "includedData"):
        parts.append(f"includedData={quote(inc, safe='')}")
    if params.get("locale"):
        parts.append(f"locale={quote(str(params['locale']).strip(), safe='')}")
    return "&".join(parts)


def main() -> None:
    params = load_cli_params()
    if not params:
        print(
            "Usage: get_catalog_item.py '<JSON>'\n"
            "Required: sellerId, region, asin, marketplaceIds\n"
            f"Optional: includedData, locale, catalogItemsVersion ({CATALOG_ITEMS_V2022}|{CATALOG_ITEMS_V2020})",
            file=sys.stderr,
        )
        sys.exit(1)

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available("get_catalog_item.py")

    if "asin" not in params:
        print("Missing required field: asin", file=sys.stderr)
        sys.exit(1)

    seller_id, region = require_seller_region(params)
    version = resolve_catalog_items_version(params)
    asin = encode_path_segment(params["asin"])
    path = f"{catalog_items_path(version)}/{asin}"
    qs = _build_query(params)

    tokens = get_store_tokens(seller_id, region)
    if "error" in tokens or "accessToken" not in tokens:
        print(json.dumps(tokens, indent=2, ensure_ascii=False))
        sys.exit(1)

    proxy = developer_proxy_get(region, path, tokens["accessToken"], query_string=qs)
    out: dict = {
        "developerProxy": proxy,
        "resolvedPath": path,
        "queryString": qs,
        "catalogItemsVersion": version,
    }
    merge_success_json(out, proxy, "catalogItem")
    inline = lf_inline_flag()
    emit_result(out, inline)


if __name__ == "__main__":
    main()
