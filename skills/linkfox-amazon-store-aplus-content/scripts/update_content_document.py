#!/usr/bin/env python3
"""
Amazon Store — updateContentDocument (SP-API A+ Content Management v2020-11-01)

官方参考: https://developer-docs.amazon.com/sp-api/reference/updatecontentdocument

Usage:
  python update_content_document.py '{"sellerId":"A1...","region":"NA","marketplaceId":"ATVPDKIKX0DER","contentReferenceKey":"...","contentDocument":{...}}'
"""

from __future__ import annotations

import json
import sys
from urllib.parse import quote

from _spapi_aplus_common import (
    APLUS_PATH_PREFIX,
    ensure_auth_skill_available,
    run_proxy,
    resolve_marketplace_id,
    encode_path_segment,
)


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: update_content_document.py '<JSON>'\n"
            "Required: sellerId, region, marketplaceId (or marketplaceIds), contentReferenceKey, contentDocument\n"
            "Optional: skipDepCheck",
            file=sys.stderr,
        )
        sys.exit(1)
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(params, dict):
        print("JSON parameters must be an object", file=sys.stderr)
        sys.exit(1)

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available("update_content_document.py")

    for f in ("sellerId", "region", "contentReferenceKey", "contentDocument"):
        if f not in params:
            print(f"Missing required field: {f}", file=sys.stderr)
            sys.exit(1)

    try:
        mid = resolve_marketplace_id(params, "updateContentDocument")
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    cd = params["contentDocument"]
    if not isinstance(cd, dict):
        print("contentDocument must be a JSON object", file=sys.stderr)
        sys.exit(1)

    key = str(params["contentReferenceKey"]).strip()
    if not key:
        print("contentReferenceKey must be non-empty", file=sys.stderr)
        sys.exit(1)

    query_string = f"marketplaceId={quote(mid, safe='')}"
    path = f"{APLUS_PATH_PREFIX}/contentDocuments/{encode_path_segment(key)}"
    body = {"contentDocument": cd}

    seller_id = str(params["sellerId"])
    region = str(params["region"])

    run_proxy("updateContentDocument", "POST", region, path, seller_id,
              query_string, result_field="updateContentDocumentResponse", body_obj=body)


if __name__ == "__main__":
    main()
