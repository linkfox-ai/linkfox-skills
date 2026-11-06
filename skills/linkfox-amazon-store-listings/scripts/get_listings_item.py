#!/usr/bin/env python3
"""
Amazon Store — Get Listings Item (SP-API Listings Items v2021-08-01)
====================================================================

通过 LinkFox 店铺网关 **POST /spApi/developerProxy** 转发 **GET getListingsItem**，
与 `linkfox-amazon-store-report` 使用同一套通用代理接口。

官方参考: https://developer-docs.amazon.com/sp-api/reference/getlistingsitem

Usage:
  python get_listings_item.py '{
    "sellerId": "A1BCDEFGHIJK2",
    "region": "NA",
    "sku": "My-Seller-SKU-001",
    "marketplaceIds": ["ATVPDKIKX0DER"]
  }'

Optional JSON fields:
  - includedData: string[] 或逗号分隔字符串；默认不传则上游通常为 summaries
  - issueLocale: 例如 en_US（可选）
  - skipDepCheck: boolean，跳过依赖检查（默认 false）

Dependency:
  `linkfox-amazon-store-auth`（与 store-report 相同；启动时运行 check_auth_dependency.py）
"""

from typing import List, Optional

import json
import sys
from urllib.parse import quote

from _spapi_listings_common import ensure_auth_skill_available, run_proxy

LISTINGS_API_VERSION = "2021-08-01"


def _path_for_get_listings_item(seller_id: str, sku: str) -> str:
    # Path segments must be percent-encoded (SKU 可含空格、斜杠等)
    enc_seller = quote(seller_id, safe="")
    enc_sku = quote(sku, safe="")
    return f"listings/{LISTINGS_API_VERSION}/items/{enc_seller}/{enc_sku}"


def _build_query_string(
    marketplace_ids: List[str],
    included_data: Optional[object],
    issue_locale: Optional[str],
) -> str:
    parts: list[str] = []
    # 官方要求 marketplaceIds；文档常见为单站点（length ≤ 1）。多传时仅取第一个并告警。
    if not marketplace_ids:
        raise ValueError("marketplaceIds must be a non-empty array of strings")
    mid = marketplace_ids[0]
    parts.append(f"marketplaceIds={quote(mid, safe='')}")
    if len(marketplace_ids) > 1:
        print(
            "⚠️  Warning: getListingsItem marketplaceIds length is typically 1; using first only.",
            file=sys.stderr,
        )
    if included_data is not None:
        if isinstance(included_data, list):
            id_val = ",".join(included_data)
        else:
            id_val = str(included_data).strip()
        if id_val:
            parts.append(f"includedData={quote(id_val, safe='')}")
    if issue_locale:
        parts.append(f"issueLocale={quote(issue_locale, safe='')}")
    return "&".join(parts)


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: get_listings_item.py '<JSON>'\n"
            "Required: sellerId, region, sku, marketplaceIds (array with ≥1 id)\n"
            "Example: get_listings_item.py "
            '\'{"sellerId":"A1...","region":"NA","sku":"ABC-1","marketplaceIds":["ATVPDKIKX0DER"]}\'',
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

    for f in ("sellerId", "region", "sku", "marketplaceIds"):
        if f not in params:
            print(f"Missing required field: {f}", file=sys.stderr)
            sys.exit(1)

    seller_id = str(params["sellerId"])
    region = str(params["region"])
    sku = str(params["sku"])
    mids = params["marketplaceIds"]
    if isinstance(mids, str):
        marketplace_ids = [mids]
    elif isinstance(mids, list):
        marketplace_ids = [str(x) for x in mids]
    else:
        print("marketplaceIds must be a string or array of strings", file=sys.stderr)
        sys.exit(1)

    included = params.get("includedData")
    issue_locale = params.get("issueLocale")
    if issue_locale is not None:
        issue_locale = str(issue_locale)

    try:
        query_string = _build_query_string(marketplace_ids, included, issue_locale)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    path = _path_for_get_listings_item(seller_id, sku)

    run_proxy("getListingsItem", "GET", region, path, seller_id, query_string,
              result_field="listing")


if __name__ == "__main__":
    main()
