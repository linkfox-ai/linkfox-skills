#!/usr/bin/env python3
"""
SP Ad Groups List - linkfox-amazon-ads-manager
=============================================

POST sp/adGroups/list (Amazon Ads v3).

Usage:
  python list_ad_groups.py '<JSON params>'

Required:
  profileId (number), region (NA/EU/FE)

Optional filters:
  adGroupIdFilter      {"include": ["...", ...]}
  campaignIdFilter     {"include": ["...", ...]}
  stateFilter          {"include": ["ENABLED", "PAUSED", "ARCHIVED"]}
  nameFilter           {"queryTermMatchType": "BROAD_MATCH", "include": ["brand"]}

Other:
  fetchAll       bool, default true
  maxResults     int  1-100, default 100
  skipDepCheck   bool, default false

Example:
  python list_ad_groups.py '{"profileId": 1234567890, "region": "NA",
                              "campaignIdFilter": {"include": ["998877"]}}'
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from _common import (  # noqa: E402
    build_filter_body,
    ensure_auth_skill_available,
    get_access_token,
    list_sp_entities,
    parse_argv_params,
    require_fields,
    emit_result,
    lf_inline_flag,
)

ENTITY_PATH = "sp/adGroups/list"
ENTITY_CONTENT_TYPE = "application/vnd.spadgroup.v3+json"
RESPONSE_KEY = "adGroups"

FILTER_KEYS = [
    "adGroupIdFilter",
    "campaignIdFilter",
    "stateFilter",
    "nameFilter",
    "campaignTargetingTypeFilter",  # "AUTO" / "MANUAL"
]


def main() -> None:
    params = parse_argv_params(__doc__)

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available()

    require_fields(params, ["profileId", "region"])

    profile_id = int(params["profileId"])
    region = params["region"]
    fetch_all = bool(params.get("fetchAll", True))
    request_body = build_filter_body(params, FILTER_KEYS)

    access_token = get_access_token(profile_id)
    result = list_sp_entities(
        region=region,
        profile_id=profile_id,
        access_token=access_token,
        entity_path=ENTITY_PATH,
        entity_content_type=ENTITY_CONTENT_TYPE,
        response_key=RESPONSE_KEY,
        request_body=request_body,
        fetch_all=fetch_all,
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
    inline = lf_inline_flag()
    emit_result(output, inline)
    print(
        f"\n✓ Fetched {len(items)} ad groups across {output['pagesFetched']} page(s)"
        f"{' (truncated at maxPages)' if output['truncated'] else ''}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
