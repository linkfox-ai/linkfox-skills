#!/usr/bin/env python3
"""
Amazon Store — postContentDocumentAsinRelations (SP-API A+ Content Management v2020-11-01)

用请求体中的 asinSet **整体替换**该 A+ 文档关联的全部 ASIN（可增可减；移除 ASIN 会 suspend 该 ASIN 上的展示）。

官方参考: https://developer-docs.amazon.com/sp-api/reference/postcontentdocumentasinrelations

Usage:
  python post_content_document_asin_relations.py '{"sellerId":"A1...","region":"NA","marketplaceId":"ATVPDKIKX0DER","contentReferenceKey":"...","asinSet":["B0...","B0..."]}'
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
    encode_path_segment,
    merge_success_json,
    emit_result,
    lf_inline_flag,
)


def _norm_asin_set(val: object) -> object:
    if isinstance(val, str):
        return [x.strip() for x in val.split(",") if x.strip()]
    if isinstance(val, list):
        if not val:
            return []
        if all(isinstance(x, dict) for x in val):
            return val
        return [str(x).strip() for x in val if str(x).strip()]
    raise ValueError(
        "asinSet must be a string, comma-separated string, array of ASIN strings, or array of objects (Amazon schema)"
    )


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: post_content_document_asin_relations.py '<JSON>'\n"
            "Required: sellerId, region, marketplaceId (or marketplaceIds), contentReferenceKey, asinSet (array or comma string)\n"
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
        ensure_auth_skill_available("post_content_document_asin_relations.py")

    for f in ("sellerId", "region", "contentReferenceKey", "asinSet"):
        if f not in params:
            print(f"Missing required field: {f}", file=sys.stderr)
            sys.exit(1)

    try:
        mid = resolve_marketplace_id(params, "postContentDocumentAsinRelations")
        asin_payload = _norm_asin_set(params["asinSet"])
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    key = str(params["contentReferenceKey"]).strip()
    if not key:
        print("contentReferenceKey must be non-empty", file=sys.stderr)
        sys.exit(1)

    query_string = f"marketplaceId={quote(mid, safe='')}"
    path = f"{APLUS_PATH_PREFIX}/contentDocuments/{encode_path_segment(key)}/asins"
    body = {"asinSet": asin_payload}

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
    merge_success_json(out, proxy, "postContentDocumentAsinRelationsResponse")
    inline = lf_inline_flag()
    emit_result(out, inline)


if __name__ == "__main__":
    main()
