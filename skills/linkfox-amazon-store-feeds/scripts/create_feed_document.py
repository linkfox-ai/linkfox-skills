#!/usr/bin/env python3
"""
Amazon Store — createFeedDocument (SP-API Feeds v2021-06-30)
============================================================

POST `feeds/2021-06-30/documents`

官方参考: https://developer-docs.amazon.com/sp-api/reference/createfeeddocument

Usage:
  python create_feed_document.py '{"sellerId":"A1...","region":"NA","contentType":"text/tab-separated-values; charset=UTF-8"}'
"""

from __future__ import annotations

import json
import sys

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
)


def main() -> None:
    params = load_cli_params()
    if not params:
        print(
            "Usage: create_feed_document.py '<JSON>'\nRequired: sellerId, region, contentType",
            file=sys.stderr,
        )
        sys.exit(1)

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available("create_feed_document.py")

    if "contentType" not in params:
        print("Missing required field: contentType", file=sys.stderr)
        sys.exit(1)

    seller_id, region = require_seller_region(params)
    path = f"{FEEDS_PATH_PREFIX}/documents"
    body_obj = {"contentType": str(params["contentType"]).strip()}
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
    merge_success_json(out, proxy, "feedDocument")
    inline = lf_inline_flag()
    emit_result(out, inline)


if __name__ == "__main__":
    main()
