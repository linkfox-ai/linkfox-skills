#!/usr/bin/env python3
"""
Amazon Store — Patch Listings Item (SP-API Listings Items v2021-08-01)
======================================================================

通过 LinkFox **POST /spApi/developerProxy** 转发 **PATCH patchListingsItem**，
与 get/search 相同：传入 sellerId + region，并带 **body**（JSON 字符串）调用代理。

官方参考: https://developer-docs.amazon.com/sp-api/reference/patchlistingsitem

Usage:
  python patch_listings_item.py '{
    "sellerId": "A1BCDEFGHIJK2",
    "region": "NA",
    "sku": "My-Seller-SKU-001",
    "marketplaceIds": ["ATVPDKIKX0DER"],
    "productType": "PRODUCT",
    "patches": [
      {"op": "replace", "path": "/attributes/item_name", "value": [{"value": "New Title", "marketplace_id": "ATVPDKIKX0DER"}]}
    ]
  }'

说明：path / value 须符合 Amazon 对该 productType 的 JSON Patch 与属性 schema；上例仅演示结构，请按实网/官方 schema 填写。

Optional JSON:
  includedData, mode (VALIDATION_PREVIEW), issueLocale, skipDepCheck
"""

from typing import Any, Dict, List, Optional

import json
import sys
from urllib.parse import quote

from _spapi_listings_common import ensure_auth_skill_available, run_proxy

LISTINGS_API_VERSION = "2021-08-01"
PATCH_OPS = frozenset({"add", "replace", "merge", "delete"})


def _path_patch(seller_id: str, sku: str) -> str:
    return (
        f"listings/{LISTINGS_API_VERSION}/items/"
        f"{quote(seller_id, safe='')}/{quote(sku, safe='')}"
    )


def _norm_marketplace_ids(val: object) -> List[str]:
    if isinstance(val, str):
        return [x.strip() for x in val.split(",") if x.strip()]
    if isinstance(val, list):
        return [str(x).strip() for x in val if str(x).strip()]
    raise ValueError("marketplaceIds must be a string or non-empty array")


def _build_patch_query(params: dict) -> str:
    mids = _norm_marketplace_ids(params["marketplaceIds"])
    if not mids:
        raise ValueError("marketplaceIds is required")
    parts: List[str] = [f"marketplaceIds={quote(','.join(mids), safe='')}"]

    inc = params.get("includedData")
    if inc is not None:
        if isinstance(inc, list):
            iv = ",".join(str(x) for x in inc)
        else:
            iv = str(inc).strip()
        if iv:
            parts.append(f"includedData={quote(iv, safe='')}")

    mode = params.get("mode")
    if mode is not None and str(mode).strip():
        parts.append(f"mode={quote(str(mode).strip(), safe='')}")

    il = params.get("issueLocale")
    if il is not None and str(il).strip():
        parts.append(f"issueLocale={quote(str(il).strip(), safe='')}")

    return "&".join(parts)


def _validate_patches(patches: object) -> List[Dict[str, Any]]:
    if not isinstance(patches, list) or len(patches) < 1:
        raise ValueError("patches must be a non-empty array (Amazon: length >= 1)")
    out: List[Dict[str, Any]] = []
    for i, p in enumerate(patches):
        if not isinstance(p, dict):
            raise ValueError(f"patches[{i}] must be an object")
        op = p.get("op")
        path_v = p.get("path")
        if not op or not path_v:
            raise ValueError(f"patches[{i}] requires 'op' and 'path'")
        if str(op) not in PATCH_OPS:
            raise ValueError(
                f"patches[{i}].op must be one of {sorted(PATCH_OPS)} (RFC 6902 subset per Amazon)"
            )
        out.append(p)
    return out


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: patch_listings_item.py '<JSON>'\n"
            "Required: sellerId, region, sku, marketplaceIds, productType, patches (array)\n"
            "Optional: includedData, mode (e.g. VALIDATION_PREVIEW), issueLocale\n"
            "See https://developer-docs.amazon.com/sp-api/reference/patchlistingsitem",
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

    for f in ("sellerId", "region", "sku", "marketplaceIds", "productType", "patches"):
        if f not in params:
            print(f"Missing required field: {f}", file=sys.stderr)
            sys.exit(1)

    seller_id = str(params["sellerId"])
    region = str(params["region"])
    sku = str(params["sku"])
    product_type = str(params["productType"])

    try:
        patches = _validate_patches(params["patches"])
        query_string = _build_patch_query(params)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    body_obj: Dict[str, Any] = {"productType": product_type, "patches": patches}

    path = _path_patch(seller_id, sku)
    run_proxy("patchListingsItem", "PATCH", region, path, seller_id, query_string,
              result_field="patchResult", body_obj=body_obj)


if __name__ == "__main__":
    main()
