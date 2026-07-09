#!/usr/bin/env python3
"""
Amazon Store — getFeeds (SP-API Feeds v2021-06-30)
==================================================

GET `feeds/2021-06-30/feeds`。须传 feedTypes 或 nextToken（分页时仅 nextToken）。

官方参考: https://developer-docs.amazon.com/sp-api/reference/getfeeds
"""

from __future__ import annotations

import json
import sys
from urllib.parse import quote

from _spapi_feeds_common import (
    FEEDS_PATH_PREFIX,
    developer_proxy_call,
    emit_result,
    ensure_auth_skill_available,
    get_store_tokens,
    lf_inline_flag,
    load_cli_params,
    merge_success_json,
    require_seller_region,
    str_list,
)


def _build_query(params: dict) -> str:
    parts: list[str] = []
    nt = params.get("nextToken")
    if nt:
        return f"nextToken={quote(str(nt).strip(), safe='')}"

    feed_types = str_list(params.get("feedTypes"), "feedTypes")
    if not feed_types:
        print("Required: feedTypes (array) or nextToken for pagination.", file=sys.stderr)
        sys.exit(1)
    if len(feed_types) > 10:
        print("feedTypes length must be ≤ 10", file=sys.stderr)
        sys.exit(1)

    def add(k: str, v: str) -> None:
        parts.append(f"{k}={quote(v, safe='')}")

    for ft in feed_types:
        add("feedTypes", ft)
    for mid in str_list(params.get("marketplaceIds"), "marketplaceIds"):
        add("marketplaceIds", mid)
    for ps in str_list(params.get("processingStatuses"), "processingStatuses"):
        add("processingStatuses", ps)
    if params.get("createdSince"):
        add("createdSince", str(params["createdSince"]).strip())
    if params.get("createdUntil"):
        add("createdUntil", str(params["createdUntil"]).strip())
    if params.get("pageSize") is not None:
        add("pageSize", str(int(params["pageSize"])))
    return "&".join(parts)


def main() -> None:
    params = load_cli_params()
    if not params:
        print(
            "Usage: get_feeds.py '<JSON>'\n"
            "Required: sellerId, region, and feedTypes OR nextToken\n"
            "Optional: marketplaceIds, processingStatuses, createdSince, createdUntil, pageSize",
            file=sys.stderr,
        )
        sys.exit(1)

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available("get_feeds.py")

    seller_id, region = require_seller_region(params)
    path = f"{FEEDS_PATH_PREFIX}/feeds"
    qs = _build_query(params)

    tokens = get_store_tokens(seller_id, region)
    if "error" in tokens or "accessToken" not in tokens:
        print(json.dumps(tokens, indent=2, ensure_ascii=False))
        sys.exit(1)

    proxy = developer_proxy_call(
        region, path, "GET", tokens["accessToken"], query_string=qs
    )
    out: dict = {"developerProxy": proxy, "resolvedPath": path, "queryString": qs}
    merge_success_json(out, proxy, "feeds")
    inline = lf_inline_flag()
    emit_result(out, inline)


if __name__ == "__main__":
    main()
