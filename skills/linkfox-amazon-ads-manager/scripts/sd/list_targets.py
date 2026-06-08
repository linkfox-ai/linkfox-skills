#!/usr/bin/env python3
"""
SD Targeting Clauses List - linkfox-amazon-ads-manager
=====================================================

GET /sd/targets (Sponsored Display v3).
返回 SD 商品 / 受众定向子句（targetingClauses）。

Usage:
  python list_targets.py '<JSON params>'

Required:
  profileId (number), region (NA/EU/FE)

Optional filters:
  targetIdFilter      {"include": ["...", ...]}
  adGroupIdFilter     {"include": ["...", ...]}
  campaignIdFilter    {"include": ["...", ...]}
  stateFilter         {"include": ["ENABLED", "PAUSED", "ARCHIVED"]}（提交上游时自动转小写）

Other:
  fetchAll                    bool, default true
  maxResults                  int  1-100, default 100（每页大小，对应 SD 端 count）
  includeExtendedDataFields   bool, default false（true 时请求 /sd/targets/extended）
  skipDepCheck                bool, default false

Notes:
  /sd/targets 上游接口不接受 expressionTypeFilter；返回字段含 expressionType（auto / manual）
  与 expression（type 如 asinSameAs / asinCategorySameAs / audience / views / purchases ...）。
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from _common import (  # noqa: E402
    DEFAULT_PAGE_SIZE,
    build_sd_query,
    ensure_auth_skill_available,
    get_access_token,
    list_sd_entities,
    parse_argv_params,
    require_fields,
)

ENTITY_PATH_BASIC = "sd/targets"
ENTITY_PATH_EXTENDED = "sd/targets/extended"
# Amazon SD targets 返回 TargetingClause 数组；输出统一以 targetingClauses 为键
RESPONSE_KEY = "targetingClauses"

FILTER_KEYS = [
    "targetIdFilter",
    "adGroupIdFilter",
    "campaignIdFilter",
    "stateFilter",
]


def main() -> None:
    params = parse_argv_params(__doc__)

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available()

    require_fields(params, ["profileId", "region"])

    profile_id = int(params["profileId"])
    region = params["region"]
    fetch_all = bool(params.get("fetchAll", True))
    page_size = int(params.get("maxResults") or DEFAULT_PAGE_SIZE)

    server_query, use_extended, _client_filters = build_sd_query(params, FILTER_KEYS)
    entity_path = ENTITY_PATH_EXTENDED if use_extended else ENTITY_PATH_BASIC

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
    output = {
        "success": True,
        RESPONSE_KEY: items,
        "total": len(items),
        "pagesFetched": result.get("pagesFetched", 0),
        "truncated": result.get("truncated", False),
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))
    print(
        f"\n✓ Fetched {len(items)} SD targeting clauses across {output['pagesFetched']} page(s)"
        f"{' (truncated at maxPages)' if output['truncated'] else ''}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
