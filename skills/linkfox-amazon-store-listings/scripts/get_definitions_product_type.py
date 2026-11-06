#!/usr/bin/env python3
"""
Amazon Store — Get Definitions Product Type (SP-API Product Type Definitions v2020-09-01)
==========================================================================================

通过 LinkFox **POST /spApi/developerProxy** 转发 **GET getDefinitionsProductType**，
获取指定 Amazon product type 的 JSON Schema 定义。

官方参考: https://developer-docs.amazon.com/sp-api/reference/getdefinitionsproducttype

Usage:
  python get_definitions_product_type.py '{
    "sellerId": "A1BCDEFGHIJK2",
    "region": "NA",
    "productType": "LUGGAGE",
    "marketplaceIds": ["ATVPDKIKX0DER"]
  }'

Optional JSON:
  querySellerId → 写入 Query 的 sellerId（卖家专属 schema；可选，常与授权店铺的 sellerId 相同）
  productTypeVersion, requirements, requirementsEnforced, locale, skipDepCheck
"""

from typing import List

import json
import sys
from urllib.parse import quote

from _spapi_listings_common import ensure_auth_skill_available, run_proxy

DEFINITIONS_API_VERSION = "2020-09-01"


def _norm_marketplace_ids(val: object) -> List[str]:
    if isinstance(val, str):
        return [x.strip() for x in val.split(",") if x.strip()]
    if isinstance(val, list):
        return [str(x).strip() for x in val if str(x).strip()]
    raise ValueError("marketplaceIds must be a string or non-empty array")


def _path_for_product_type(product_type: str) -> str:
    enc = quote(product_type.strip(), safe="")
    return f"definitions/{DEFINITIONS_API_VERSION}/productTypes/{enc}"


def _build_query(params: dict) -> str:
    mids = _norm_marketplace_ids(params["marketplaceIds"])
    if not mids:
        raise ValueError("marketplaceIds is required")
    if len(mids) > 1:
        raise ValueError(
            "getDefinitionsProductType: marketplaceIds is limited to one id at this time (Amazon)"
        )
    parts: List[str] = [f"marketplaceIds={quote(mids[0], safe='')}"]

    qs = params.get("querySellerId")
    if qs is not None and str(qs).strip():
        parts.append(f"sellerId={quote(str(qs).strip(), safe='')}")

    ptv = params.get("productTypeVersion")
    if ptv is not None and str(ptv).strip():
        parts.append(f"productTypeVersion={quote(str(ptv).strip(), safe='')}")

    req = params.get("requirements")
    if req is not None and str(req).strip():
        parts.append(f"requirements={quote(str(req).strip(), safe='')}")

    re_ = params.get("requirementsEnforced")
    if re_ is not None and str(re_).strip():
        parts.append(f"requirementsEnforced={quote(str(re_).strip(), safe='')}")

    loc = params.get("locale")
    if loc is not None and str(loc).strip():
        parts.append(f"locale={quote(str(loc).strip(), safe='')}")

    return "&".join(parts)


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: get_definitions_product_type.py '<JSON>'\n"
            "Required: sellerId (已授权店铺), region, productType, marketplaceIds (exactly one id)\n"
            "Optional: querySellerId → Query sellerId; productTypeVersion; requirements; "
            "requirementsEnforced; locale\n"
            "See https://developer-docs.amazon.com/sp-api/reference/getdefinitionsproducttype",
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

    for f in ("sellerId", "region", "productType", "marketplaceIds"):
        if f not in params:
            print(f"Missing required field: {f}", file=sys.stderr)
            sys.exit(1)

    seller_id = str(params["sellerId"])
    region = str(params["region"])
    product_type = str(params["productType"]).strip()
    if not product_type:
        print("productType must be non-empty", file=sys.stderr)
        sys.exit(1)

    try:
        query_string = _build_query(params)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    path = _path_for_product_type(product_type)
    run_proxy("getDefinitionsProductType", "GET", region, path, seller_id, query_string,
              result_field="productTypeDefinitionResult")


if __name__ == "__main__":
    main()
