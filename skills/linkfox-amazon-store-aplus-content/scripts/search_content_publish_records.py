#!/usr/bin/env python3
"""
Amazon Store — searchContentPublishRecords (SP-API A+ Content Management v2020-11-01)

官方参考: https://developer-docs.amazon.com/sp-api/reference/searchcontentpublishrecords

Query 参数 asin 必填（文档 length ≥ 10）。

Usage:
  python search_content_publish_records.py '{"sellerId":"A1...","region":"NA","marketplaceId":"ATVPDKIKX0DER","asin":"B0XXXXXXXXXX"}'
"""

from __future__ import annotations

import json
import sys
from urllib.parse import quote

from _spapi_aplus_common import (
    APLUS_PATH_PREFIX,
    ensure_auth_skill_available,
    get_store_tokens,
    developer_proxy_get,
    resolve_marketplace_id,
    merge_success_json,
    emit_result,
    lf_inline_flag,
)


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: search_content_publish_records.py '<JSON>'\n"
            "Required: sellerId, region, marketplaceId (or marketplaceIds), asin (length ≥ 10)\n"
            "Optional: pageToken, skipDepCheck",
            file=sys.stderr,
        )
        sys.exit(1)
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available("search_content_publish_records.py")

    for f in ("sellerId", "region", "asin"):
        if f not in params:
            print(f"Missing required field: {f}", file=sys.stderr)
            sys.exit(1)

    try:
        mid = resolve_marketplace_id(params, "searchContentPublishRecords")
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    asin = str(params["asin"]).strip()
    if len(asin) < 10:
        print("asin must be at least 10 characters (per Amazon schema)", file=sys.stderr)
        sys.exit(1)

    parts = [
        f"marketplaceId={quote(mid, safe='')}",
        f"asin={quote(asin, safe='')}",
    ]
    pt = params.get("pageToken")
    if pt:
        parts.append(f"pageToken={quote(str(pt).strip(), safe='')}")
    query_string = "&".join(parts)
    path = f"{APLUS_PATH_PREFIX}/contentPublishRecords"

    seller_id = str(params["sellerId"])
    region = str(params["region"])

    tokens = get_store_tokens(seller_id, region)
    if "error" in tokens or "accessToken" not in tokens:
        print(json.dumps(tokens, indent=2, ensure_ascii=False))
        sys.exit(1)

    proxy = developer_proxy_get(region, path, tokens["accessToken"], query_string)
    out: dict = {
        "developerProxy": proxy,
        "resolvedPath": path,
        "queryString": query_string,
    }
    merge_success_json(out, proxy, "searchContentPublishRecordsResponse")
    inline = lf_inline_flag()
    emit_result(out, inline)


if __name__ == "__main__":
    main()
