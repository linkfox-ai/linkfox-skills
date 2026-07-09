#!/usr/bin/env python3
"""
Amazon Store — getFeedDocument (SP-API Feeds v2021-06-30)
=========================================================

GET `feeds/2021-06-30/documents/{feedDocumentId}`

官方参考: https://developer-docs.amazon.com/sp-api/reference/getfeeddocument
"""

from __future__ import annotations

import json
import sys
from urllib.parse import quote

from _spapi_feeds_common import (
    FEEDS_PATH_PREFIX,
    developer_proxy_call,
    emit_result,
    encode_path_segment,
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
            "Usage: get_feed_document.py '<JSON>'\n"
            "Required: sellerId, region, feedDocumentId\n"
            "Optional: enableContentEncodingUrlHeader (boolean)",
            file=sys.stderr,
        )
        sys.exit(1)

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available("get_feed_document.py")

    if "feedDocumentId" not in params:
        print("Missing required field: feedDocumentId", file=sys.stderr)
        sys.exit(1)

    seller_id, region = require_seller_region(params)
    doc_id = encode_path_segment(params["feedDocumentId"])
    path = f"{FEEDS_PATH_PREFIX}/documents/{doc_id}"

    qs = None
    if "enableContentEncodingUrlHeader" in params:
        flag = "true" if params["enableContentEncodingUrlHeader"] else "false"
        qs = f"enableContentEncodingUrlHeader={quote(flag, safe='')}"

    tokens = get_store_tokens(seller_id, region)
    if "error" in tokens or "accessToken" not in tokens:
        print(json.dumps(tokens, indent=2, ensure_ascii=False))
        sys.exit(1)

    proxy = developer_proxy_call(
        region, path, "GET", tokens["accessToken"], query_string=qs
    )
    out: dict = {"developerProxy": proxy, "resolvedPath": path, "queryString": qs}
    merge_success_json(out, proxy, "feedDocument")
    inline = lf_inline_flag()
    emit_result(out, inline)


if __name__ == "__main__":
    main()
