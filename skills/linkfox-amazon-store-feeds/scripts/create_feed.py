#!/usr/bin/env python3
"""
Amazon Store — createFeed (SP-API Feeds v2021-06-30)
====================================================

POST `feeds/2021-06-30/feeds`。须先 createFeedDocument 并上传文档内容。

官方参考: https://developer-docs.amazon.com/sp-api/reference/createfeed
"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict

from _spapi_feeds_common import (
    FEEDS_PATH_PREFIX,
    developer_proxy_call,
    emit_result,
    ensure_auth_skill_available,
    get_store_tokens,
    lf_inline_flag,
    load_cli_params,
    merge_success_json,
    norm_marketplace_ids,
    require_seller_region,
)


def _build_body(params: dict) -> Dict[str, Any]:
    for f in ("feedType", "inputFeedDocumentId"):
        if f not in params:
            print(f"Missing required field: {f}", file=sys.stderr)
            sys.exit(1)
    mids = norm_marketplace_ids(params)
    if not mids:
        print("Missing marketplaceIds (or marketplaceId)", file=sys.stderr)
        sys.exit(1)
    if len(mids) > 25:
        print("marketplaceIds length must be ≤ 25", file=sys.stderr)
        sys.exit(1)
    body: Dict[str, Any] = {
        "feedType": str(params["feedType"]).strip(),
        "marketplaceIds": mids,
        "inputFeedDocumentId": str(params["inputFeedDocumentId"]).strip(),
    }
    fo = params.get("feedOptions")
    if fo is not None:
        if not isinstance(fo, dict):
            print("feedOptions must be an object when provided", file=sys.stderr)
            sys.exit(1)
        body["feedOptions"] = fo
    return body


def main() -> None:
    params = load_cli_params()
    if not params:
        print(
            "Usage: create_feed.py '<JSON>'\n"
            "Required: sellerId, region, feedType, marketplaceIds, inputFeedDocumentId\n"
            "Optional: feedOptions",
            file=sys.stderr,
        )
        sys.exit(1)

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available("create_feed.py")

    seller_id, region = require_seller_region(params)
    path = f"{FEEDS_PATH_PREFIX}/feeds"
    body_obj = _build_body(params)
    body_str = json.dumps(body_obj, ensure_ascii=False)

    tokens = get_store_tokens(seller_id, region)
    if "error" in tokens or "accessToken" not in tokens:
        print(json.dumps(tokens, indent=2, ensure_ascii=False))
        sys.exit(1)

    proxy = developer_proxy_call(
        region, path, "POST", tokens["accessToken"], body=body_str
    )
    out: dict = {
        "developerProxy": proxy,
        "resolvedPath": path,
        "requestBody": body_obj,
    }
    merge_success_json(out, proxy, "feed")
    inline = lf_inline_flag()
    emit_result(out, inline)


if __name__ == "__main__":
    main()
