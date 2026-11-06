#!/usr/bin/env python3
"""
Amazon Store — validateContentDocumentAsinRelations (SP-API A+ Content Management v2020-11-01)

官方参考: https://developer-docs.amazon.com/sp-api/reference/validatecontentdocumentasinrelations

Usage:
  python validate_content_document_asin_relations.py '{"sellerId":"A1...","region":"NA","marketplaceId":"ATVPDKIKX0DER","contentDocument":{...},"asinSet":["B0..."]}'
  # asinSet 可选；也可仅放在 Query（本脚本支持 body 外再传 query asinSet）
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
)


def _append_asin_query(parts: list[str], asin_set: object | None) -> None:
    if asin_set is None:
        return
    if isinstance(asin_set, str):
        vals = [x.strip() for x in asin_set.split(",") if x.strip()]
    elif isinstance(asin_set, list):
        vals = [str(x).strip() for x in asin_set if str(x).strip()]
    else:
        raise ValueError("asinSet must be string, comma string, or array")
    if vals:
        parts.append(f"asinSet={quote(','.join(vals), safe=',')}")


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: validate_content_document_asin_relations.py '<JSON>'\n"
            "Required: sellerId, region, marketplaceId (or marketplaceIds), contentDocument\n"
            "Optional: asinSet (写入 Query，与官方文档一致), skipDepCheck",
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
        ensure_auth_skill_available("validate_content_document_asin_relations.py")

    for f in ("sellerId", "region", "contentDocument"):
        if f not in params:
            print(f"Missing required field: {f}", file=sys.stderr)
            sys.exit(1)

    try:
        mid = resolve_marketplace_id(params, "validateContentDocumentAsinRelations")
        parts = [f"marketplaceId={quote(mid, safe='')}"]
        _append_asin_query(parts, params.get("asinSet"))
        query_string = "&".join(parts)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    cd = params["contentDocument"]
    if not isinstance(cd, dict):
        print("contentDocument must be a JSON object", file=sys.stderr)
        sys.exit(1)

    path = f"{APLUS_PATH_PREFIX}/contentAsinValidations"
    body = {"contentDocument": cd}

    seller_id = str(params["sellerId"])
    region = str(params["region"])

    run_proxy("validateContentDocumentAsinRelations", "POST", region, path, seller_id,
              query_string, result_field="validateContentDocumentAsinRelationsResponse", body_obj=body)


if __name__ == "__main__":
    main()
