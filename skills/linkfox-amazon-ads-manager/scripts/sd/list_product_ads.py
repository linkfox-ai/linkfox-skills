#!/usr/bin/env python3
"""
SD Product Ads List - linkfox-amazon-ads-manager
===============================================

GET /sd/productAds (Sponsored Display v3).

Usage:
  python list_product_ads.py '<JSON params>'

Required:
  profileId (number), region (NA/EU/FE)

Optional filters:
  adIdFilter         {"include": ["...", ...]}
  adGroupIdFilter    {"include": ["...", ...]}
  campaignIdFilter   {"include": ["...", ...]}
  stateFilter        {"include": ["ENABLED", "PAUSED", "ARCHIVED"]}（提交上游时自动转小写）
  asinFilter         {"include": ["B01ABCDEFG", ...]}   ← Client-side filter
  skuFilter          {"include": ["SKU-123", ...]}      ← Client-side filter

Other:
  fetchAll                    bool, default true
  maxResults                  int  1-100, default 100（每页大小，对应 SD 端 count）
  includeExtendedDataFields   bool, default false（true 时请求 /sd/productAds/extended）
  skipDepCheck                bool, default false

Notes (client-side filter):
  Sponsored Display 的 /sd/productAds 接口不支持按 ASIN / SKU 过滤；脚本会先按其他过滤条件
  拉取 productAds，再在本地按精确值匹配。建议同时传 campaignIdFilter / adGroupIdFilter 收窄
  上游拉取范围以获得更好性能。

Example (按 ASIN 反查 SD 广告):
  python list_product_ads.py '{"profileId": 1234567890, "region": "NA",
                                "asinFilter": {"include": ["B01ABCDEFG"]},
                                "stateFilter": {"include": ["ENABLED"]}}'
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from _common import (  # noqa: E402
    DEFAULT_PAGE_SIZE,
    apply_client_side_filters,
    build_sd_query,
    ensure_auth_skill_available,
    get_access_token,
    list_sd_entities,
    parse_argv_params,
    require_fields,
)

ENTITY_PATH_BASIC = "sd/productAds"
ENTITY_PATH_EXTENDED = "sd/productAds/extended"
RESPONSE_KEY = "productAds"

FILTER_KEYS = [
    "adIdFilter",
    "adGroupIdFilter",
    "campaignIdFilter",
    "stateFilter",
    "asinFilter",       # client-side
    "skuFilter",        # client-side
]

SERVER_NARROWING_FILTERS = ("adIdFilter", "adGroupIdFilter", "campaignIdFilter")


def main() -> None:
    params = parse_argv_params(__doc__)

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available()

    require_fields(params, ["profileId", "region"])

    profile_id = int(params["profileId"])
    region = params["region"]
    fetch_all = bool(params.get("fetchAll", True))
    page_size = int(params.get("maxResults") or DEFAULT_PAGE_SIZE)

    server_query, use_extended, client_filters = build_sd_query(params, FILTER_KEYS)
    entity_path = ENTITY_PATH_EXTENDED if use_extended else ENTITY_PATH_BASIC

    if client_filters and not any(k in server_query for k in SERVER_NARROWING_FILTERS):
        keys = ", ".join(client_filters.keys())
        print(
            f"⚠️  使用 {keys} 但未同时传 adIdFilter/adGroupIdFilter/campaignIdFilter 收窄范围；"
            "将在客户端过滤所有 SD productAds，可能较慢。"
            "建议配合 campaignIdFilter 或 adGroupIdFilter 使用以获得更好性能。",
            file=sys.stderr,
        )

    access_token = get_access_token(profile_id)
    result = list_sd_entities(
        region=region,
        profile_id=profile_id,
        access_token=access_token,
        entity_path=entity_path,
        response_key=RESPONSE_KEY,
        server_query=server_query,
        fetch_all=fetch_all,
        page_size=page_size,
    )

    if "error" in result:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(1)

    items = result.get("items", [])
    server_total = len(items)
    if client_filters:
        items = apply_client_side_filters(items, client_filters)

    output = {
        "success": True,
        RESPONSE_KEY: items,
        "total": len(items),
        "pagesFetched": result.get("pagesFetched", 0),
        "truncated": result.get("truncated", False),
    }
    if client_filters:
        output["serverTotalBeforeClientFilter"] = server_total
        output["clientSideFilters"] = {k: v for k, v in client_filters.items()}
    print(json.dumps(output, indent=2, ensure_ascii=False))

    if client_filters:
        print(
            f"\n✓ Fetched {server_total} SD product ads from upstream, "
            f"filtered to {len(items)} by {list(client_filters.keys())}",
            file=sys.stderr,
        )
    else:
        print(
            f"\n✓ Fetched {len(items)} SD product ads across {output['pagesFetched']} page(s)"
            f"{' (truncated at maxPages)' if output['truncated'] else ''}",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
