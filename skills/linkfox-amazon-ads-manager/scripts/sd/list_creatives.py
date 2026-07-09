#!/usr/bin/env python3
"""
SD Creatives List - linkfox-amazon-ads-manager
=============================================

GET /sd/creatives (Sponsored Display v3).
返回 SD 创意素材列表。

Usage:
  python list_creatives.py '<JSON params>'

Required:
  profileId (number), region (NA/EU/FE)

Optional filters:
  creativeIdFilter        {"include": ["...", ...]}
  adGroupIdFilter         {"include": ["...", ...]}

Other:
  fetchAll                bool, default true
  maxResults              int  1-100, default 100（每页大小，对应 SD 端 count，上限 100）
  skipDepCheck            bool, default false

Notes:
  - /sd/creatives 接口规定 creativeIdFilter 与 adGroupIdFilter 互斥；同时传时脚本仅在
    stderr 输出提示，仍透传上游，由 Amazon Ads 按 400 / 422 返回。
  - /sd/creatives 没有 /extended 路径，`includeExtendedDataFields` 入参对本接口无效。
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
    emit_result,
    lf_inline_flag,
)

ENTITY_PATH = "sd/creatives"
RESPONSE_KEY = "creatives"

FILTER_KEYS = [
    "creativeIdFilter",
    "adGroupIdFilter",
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

    server_query, _use_extended, _client_filters = build_sd_query(params, FILTER_KEYS)

    if "creativeIdFilter" in server_query and "adGroupIdFilter" in server_query:
        print(
            "⚠️  /sd/creatives 接口规定 creativeIdFilter 与 adGroupIdFilter 互斥；"
            "同时传两者上游通常会返回 400 / 422。",
            file=sys.stderr,
        )

    access_token = get_access_token(profile_id)
    result = list_sd_entities(
        region=region,
        profile_id=profile_id,
        access_token=access_token,
        entity_path=ENTITY_PATH,
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
    inline = lf_inline_flag()
    emit_result(output, inline)
    print(
        f"\n✓ Fetched {len(items)} SD creatives across {output['pagesFetched']} page(s)"
        f"{' (truncated at maxPages)' if output['truncated'] else ''}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
