#!/usr/bin/env python3
"""
Amazon Store — listContentDocumentAsinRelations (SP-API A+ Content Management v2020-11-01)

官方参考: https://developer-docs.amazon.com/sp-api/reference/listcontentdocumentasinrelations

Usage:
  python list_content_document_asin_relations.py '{"sellerId":"A1...","region":"NA","marketplaceId":"ATVPDKIKX0DER","contentReferenceKey":"..."}'
  # 可选: includedDataSet, asinSet, pageToken
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
    encode_path_segment,
    merge_success_json,
    emit_result,
    lf_inline_flag,
)


def _append_asin_set(parts: list[str], asin_set: object | None) -> None:
    if asin_set is None:
        return
    if isinstance(asin_set, str):
        vals = [x.strip() for x in asin_set.split(",") if x.strip()]
    elif isinstance(asin_set, list):
        vals = [str(x).strip() for x in asin_set if str(x).strip()]
    else:
        raise ValueError("asinSet must be string, comma string, or array")
    for a in vals:
        parts.append(f"asinSet={quote(a, safe='')}")


def _append_included(parts: list[str], included: object | None) -> None:
    if included is None:
        return
    if isinstance(included, str):
        vals = [x.strip() for x in included.split(",") if x.strip()]
    elif isinstance(included, list):
        vals = [str(x).strip() for x in included if str(x).strip()]
    else:
        raise ValueError("includedDataSet must be string, comma string, or array")
    for v in vals:
        parts.append(f"includedDataSet={quote(v, safe='')}")


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: list_content_document_asin_relations.py '<JSON>'\n"
            "Required: sellerId, region, marketplaceId (or marketplaceIds), contentReferenceKey\n"
            "Optional: includedDataSet, asinSet, pageToken, skipDepCheck",
            file=sys.stderr,
        )
        sys.exit(1)
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available("list_content_document_asin_relations.py")

    for f in ("sellerId", "region", "contentReferenceKey"):
        if f not in params:
            print(f"Missing required field: {f}", file=sys.stderr)
            sys.exit(1)

    try:
        mid = resolve_marketplace_id(params, "listContentDocumentAsinRelations")
        parts = [f"marketplaceId={quote(mid, safe='')}"]
        _append_included(parts, params.get("includedDataSet"))
        _append_asin_set(parts, params.get("asinSet"))
        pt = params.get("pageToken")
        if pt:
            parts.append(f"pageToken={quote(str(pt).strip(), safe='')}")
        query_string = "&".join(parts)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    key = str(params["contentReferenceKey"]).strip()
    if not key:
        print("contentReferenceKey must be non-empty", file=sys.stderr)
        sys.exit(1)

    path = f"{APLUS_PATH_PREFIX}/contentDocuments/{encode_path_segment(key)}/asins"

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
    merge_success_json(out, proxy, "listContentDocumentAsinRelationsResponse")
    inline = lf_inline_flag()
    emit_result(out, inline)


if __name__ == "__main__":
    main()
