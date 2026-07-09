#!/usr/bin/env python3
"""
Amazon Store — cancelFeed (SP-API Feeds v2021-06-30)
====================================================

DELETE `feeds/2021-06-30/feeds/{feedId}`

官方参考: https://developer-docs.amazon.com/sp-api/reference/cancelfeed
"""

from __future__ import annotations

import json
import sys

from _spapi_feeds_common import (
    FEEDS_PATH_PREFIX,
    developer_proxy_call,
    emit_result,
    encode_path_segment,
    ensure_auth_skill_available,
    get_store_tokens,
    lf_inline_flag,
    load_cli_params,
    require_seller_region,
)


def main() -> None:
    params = load_cli_params()
    if not params:
        print(
            "Usage: cancel_feed.py '<JSON>'\nRequired: sellerId, region, feedId",
            file=sys.stderr,
        )
        sys.exit(1)

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available("cancel_feed.py")

    if "feedId" not in params:
        print("Missing required field: feedId", file=sys.stderr)
        sys.exit(1)

    seller_id, region = require_seller_region(params)
    path = f"{FEEDS_PATH_PREFIX}/feeds/{encode_path_segment(params['feedId'])}"

    tokens = get_store_tokens(seller_id, region)
    if "error" in tokens or "accessToken" not in tokens:
        print(json.dumps(tokens, indent=2, ensure_ascii=False))
        sys.exit(1)

    proxy = developer_proxy_call(region, path, "DELETE", tokens["accessToken"])
    out: dict = {"developerProxy": proxy, "resolvedPath": path}
    inline = lf_inline_flag()
    emit_result(out, inline)


if __name__ == "__main__":
    main()
