#!/usr/bin/env python3
"""
Amazon Store — searchContentDocuments (SP-API A+ Content Management v2020-11-01)

官方参考: https://developer-docs.amazon.com/sp-api/reference/searchcontentdocuments

Usage:
  python search_content_documents.py '{"sellerId":"A1...","region":"NA","marketplaceId":"ATVPDKIKX0DER"}'
  python search_content_documents.py '{"sellerId":"A1...","region":"NA","marketplaceIds":["ATVPDKIKX0DER"],"pageToken":"..."}'
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


def _build_query(marketplace_id: str, page_token: str | None) -> str:
    parts = [f"marketplaceId={quote(marketplace_id, safe='')}"]
    if page_token:
        parts.append(f"pageToken={quote(page_token, safe='')}")
    return "&".join(parts)


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: search_content_documents.py '<JSON>'\n"
            "Required: sellerId, region, marketplaceId (or marketplaceIds)\n"
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
        ensure_auth_skill_available("search_content_documents.py")

    for f in ("sellerId", "region"):
        if f not in params:
            print(f"Missing required field: {f}", file=sys.stderr)
            sys.exit(1)

    try:
        mid = resolve_marketplace_id(params, "searchContentDocuments")
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    page_token = params.get("pageToken")
    if page_token is not None:
        page_token = str(page_token).strip() or None

    query_string = _build_query(mid, page_token)
    path = f"{APLUS_PATH_PREFIX}/contentDocuments"

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
    merge_success_json(out, proxy, "searchContentDocumentsResponse")
    inline = lf_inline_flag()
    emit_result(out, inline)


if __name__ == "__main__":
    main()
