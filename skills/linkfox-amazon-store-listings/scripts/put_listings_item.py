#!/usr/bin/env python3
"""
Amazon Store — Put Listings Item (SP-API Listings Items v2021-08-01)
===================================================================

通过 LinkFox **POST /spApi/developerProxy** 转发 **PUT putListingsItem**，
创建新刊登或对现有刊登做**全量**更新；与 get/patch 相同：传入 sellerId + region，并带 **body**（JSON 字符串）调用代理。

官方参考: https://developer-docs.amazon.com/sp-api/reference/putlistingsitem

Usage:
  python put_listings_item.py '{
    "sellerId": "A1BCDEFGHIJK2",
    "region": "NA",
    "sku": "My-Seller-SKU-001",
    "marketplaceIds": ["ATVPDKIKX0DER"],
    "productType": "LUGGAGE",
    "requirements": "LISTING",
    "attributes": { "item_name": [ { "value": "Title", "marketplace_id": "ATVPDKIKX0DER" } ] }
  }'

说明：`attributes` 须符合该 productType 的 JSON Schema；上例仅演示结构。

Optional JSON:
  includedData, mode (VALIDATION_PREVIEW), issueLocale, skipDepCheck
"""

from typing import Any, Dict, List

import json
import sys
from urllib.parse import quote

from _spapi_listings_common import ensure_auth_skill_available, run_proxy

LISTINGS_API_VERSION = "2021-08-01"
REQUIREMENTS_SET = frozenset({"LISTING", "LISTING_PRODUCT_ONLY", "LISTING_OFFER_ONLY"})


def _path_put(seller_id: str, sku: str) -> str:
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


def _build_put_query(params: dict) -> str:
    mids = _norm_marketplace_ids(params["marketplaceIds"])
    if not mids:
        raise ValueError("marketplaceIds is required")
    if len(mids) > 1:
        raise ValueError(
            "putListingsItem requires at most one marketplace id (Amazon: marketplaceIds length ≤ 1)"
        )
    parts: List[str] = [f"marketplaceIds={quote(mids[0], safe='')}"]

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


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: put_listings_item.py '<JSON>'\n"
            "Required: sellerId, region, sku, marketplaceIds (exactly one id), "
            "productType, requirements, attributes (object)\n"
            "requirements: LISTING | LISTING_PRODUCT_ONLY | LISTING_OFFER_ONLY\n"
            "Optional: includedData, mode (e.g. VALIDATION_PREVIEW), issueLocale\n"
            "See https://developer-docs.amazon.com/sp-api/reference/putlistingsitem",
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

    for f in ("sellerId", "region", "sku", "marketplaceIds", "productType", "requirements", "attributes"):
        if f not in params:
            print(f"Missing required field: {f}", file=sys.stderr)
            sys.exit(1)

    seller_id = str(params["sellerId"])
    region = str(params["region"])
    sku = str(params["sku"])
    product_type = str(params["productType"])
    requirements = str(params["requirements"]).strip()

    if requirements not in REQUIREMENTS_SET:
        print(
            f"requirements must be one of {sorted(REQUIREMENTS_SET)}",
            file=sys.stderr,
        )
        sys.exit(1)

    attrs = params["attributes"]
    if not isinstance(attrs, dict):
        print("attributes must be a JSON object", file=sys.stderr)
        sys.exit(1)

    try:
        query_string = _build_put_query(params)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    body_obj: Dict[str, Any] = {
        "productType": product_type,
        "requirements": requirements,
        "attributes": attrs,
    }

    path = _path_put(seller_id, sku)
    run_proxy("putListingsItem", "PUT", region, path, seller_id, query_string,
              result_field="putResult", body_obj=body_obj)


if __name__ == "__main__":
    main()
