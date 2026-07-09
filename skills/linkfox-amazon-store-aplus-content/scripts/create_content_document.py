#!/usr/bin/env python3
"""
Amazon Store — createContentDocument (SP-API A+ Content Management v2020-11-01)

官方参考: https://developer-docs.amazon.com/sp-api/reference/createcontentdocument

Usage:
  python create_content_document.py '{"sellerId":"A1...","region":"NA","marketplaceId":"ATVPDKIKX0DER","contentDocument":{...}}'
"""

from __future__ import annotations

import json
import sys
from urllib.parse import quote

from _spapi_aplus_common import (
    APLUS_PATH_PREFIX,
    ensure_auth_skill_available,
    get_store_tokens,
    developer_proxy_post,
    resolve_marketplace_id,
    merge_success_json,
    emit_result,
    lf_inline_flag,
)


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: create_content_document.py '<JSON>'\n"
            "Required: sellerId, region, marketplaceId (or marketplaceIds), contentDocument (object)\n"
            "Optional: skipDepCheck",
            file=sys.stderr,
        )
        sys.exit(1)
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available("create_content_document.py")

    for f in ("sellerId", "region", "contentDocument"):
        if f not in params:
            print(f"Missing required field: {f}", file=sys.stderr)
            sys.exit(1)

    try:
        mid = resolve_marketplace_id(params, "createContentDocument")
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    cd = params["contentDocument"]
    if not isinstance(cd, dict):
        print("contentDocument must be a JSON object", file=sys.stderr)
        sys.exit(1)

    query_string = f"marketplaceId={quote(mid, safe='')}"
    path = f"{APLUS_PATH_PREFIX}/contentDocuments"
    body = {"contentDocument": cd}

    seller_id = str(params["sellerId"])
    region = str(params["region"])

    tokens = get_store_tokens(seller_id, region)
    if "error" in tokens or "accessToken" not in tokens:
        print(json.dumps(tokens, indent=2, ensure_ascii=False))
        sys.exit(1)

    proxy = developer_proxy_post(
        region, path, tokens["accessToken"], query_string=query_string, body_obj=body
    )
    out: dict = {
        "developerProxy": proxy,
        "resolvedPath": path,
        "queryString": query_string,
    }
    merge_success_json(out, proxy, "createContentDocumentResponse")
    inline = lf_inline_flag()
    emit_result(out, inline)


if __name__ == "__main__":
    main()
