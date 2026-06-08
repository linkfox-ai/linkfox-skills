#!/usr/bin/env python3
"""
SP Product Ads List - linkfox-amazon-ads-manager
===============================================

POST sp/productAds/list (Sponsored Products v3).

Usage:
  python list_product_ads.py '<JSON params>'

Required:
  profileId (number), region (NA / EU / FE)

Optional filters:
  adIdFilter         {"include": ["...", ...]}
  adGroupIdFilter    {"include": ["...", ...]}
  campaignIdFilter   {"include": ["...", ...]}
  stateFilter        {"include": ["ENABLED", "PAUSED", "ARCHIVED"]}
  asinFilter         {"include": ["B01ABCDEFG", ...]}   ← 本 skill 做客户端过滤
  skuFilter          {"include": ["SKU-123", ...]}      ← 本 skill 做客户端过滤

Pagination & control:
  fetchAll       bool, default true（ASIN/SKU 过滤时强烈建议开启，否则可能找不到目标）
  maxResults     int  1-100, default 100
  skipDepCheck   bool, default false

Notes (client-side filter):
  `asinFilter` / `skuFilter` 在上游 SP list 接口并不原生生效；本 skill 的做法是把入参的 ASIN/SKU 在本地对拉回
  的结果做精确匹配过滤。因此，对 asinFilter/skuFilter 使用：
  - 建议同时带 campaignIdFilter 或 adGroupIdFilter 以缩小拉取范围，性能更好。
  - 如果只传 asinFilter，脚本会自动在 stderr 输出一次建议；返回 "total" 为客户端过滤后的条数。

Example (按 ASIN 反查广告):
  python list_product_ads.py '{"profileId": 1234567890, "region": "NA",
                                "asinFilter": {"include": ["B01ABCDEFG"]},
                                "stateFilter": {"include": ["ENABLED"]}}'
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from _common import (  # noqa: E402
    apply_client_side_filters,
    ensure_auth_skill_available,
    get_access_token,
    list_sp_entities,
    parse_argv_params,
    require_fields,
    split_server_client_filters,
)

ENTITY_PATH = "sp/productAds/list"
ENTITY_CONTENT_TYPE = "application/vnd.spproductad.v3+json"
RESPONSE_KEY = "productAds"

FILTER_KEYS = [
    "adIdFilter",
    "adGroupIdFilter",
    "campaignIdFilter",
    "stateFilter",
    "asinFilter",       # client-side
    "skuFilter",        # client-side
]

# 能在上游收窄查询范围的字段；缺这些而传 asinFilter/skuFilter 时会很慢
SERVER_NARROWING_FILTERS = ("adIdFilter", "adGroupIdFilter", "campaignIdFilter")


def main() -> None:
    params = parse_argv_params(__doc__)

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available()

    require_fields(params, ["profileId", "region"])

    profile_id = int(params["profileId"])
    region = params["region"]
    fetch_all = bool(params.get("fetchAll", True))

    server_body, client_filters = split_server_client_filters(params, FILTER_KEYS)

    # 客户端过滤无上游收窄时的性能提示
    if client_filters and not any(k in server_body for k in SERVER_NARROWING_FILTERS):
        keys = ", ".join(client_filters.keys())
        print(
            f"⚠️  使用 {keys} 但未同时传 adIdFilter/adGroupIdFilter/campaignIdFilter 收窄范围；"
            "将在客户端过滤所有 productAds，可能较慢。"
            "建议配合 campaignIdFilter 或 adGroupIdFilter 使用以获得更好性能。",
            file=sys.stderr,
        )

    access_token = get_access_token(profile_id)
    result = list_sp_entities(
        region=region,
        profile_id=profile_id,
        access_token=access_token,
        entity_path=ENTITY_PATH,
        entity_content_type=ENTITY_CONTENT_TYPE,
        response_key=RESPONSE_KEY,
        request_body=server_body,
        fetch_all=fetch_all,
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
            f"\n✓ Fetched {server_total} product ads from upstream, "
            f"filtered to {len(items)} by {list(client_filters.keys())}",
            file=sys.stderr,
        )
    else:
        print(
            f"\n✓ Fetched {len(items)} product ads across {output['pagesFetched']} page(s)"
            f"{' (truncated at maxPages)' if output['truncated'] else ''}",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
