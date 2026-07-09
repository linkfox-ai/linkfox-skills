#!/usr/bin/env python3
"""
Amazon Store — getContentDocument (SP-API A+ Content Management v2020-11-01)

官方参考: https://developer-docs.amazon.com/sp-api/reference/getcontentdocument

includedDataSet 为必填（至少一项），常见取值: CONTENTS, METADATA

Usage:
  python get_content_document.py '{"sellerId":"A1...","region":"NA","marketplaceId":"ATVPDKIKX0DER","contentReferenceKey":"...","includedDataSet":["CONTENTS","METADATA"]}'
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


def _norm_str_list(val: object, field: str) -> list[str]:
    if isinstance(val, str):
        return [x.strip() for x in val.split(",") if x.strip()]
    if isinstance(val, list):
        return [str(x).strip() for x in val if str(x).strip()]
    raise ValueError(f"{field} must be a non-empty string, comma string, or array")


def _build_query(marketplace_id: str, included_data_set: list[str]) -> str:
    parts = [f"marketplaceId={quote(marketplace_id, safe='')}"]
    for item in included_data_set:
        parts.append(f"includedDataSet={quote(item, safe='')}")
    return "&".join(parts)


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: get_content_document.py '<JSON>'\n"
            "Required: sellerId, region, marketplaceId (or marketplaceIds), contentReferenceKey, includedDataSet (array, len>=1)\n"
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
        ensure_auth_skill_available("get_content_document.py")

    for f in ("sellerId", "region", "contentReferenceKey", "includedDataSet"):
        if f not in params:
            print(f"Missing required field: {f}", file=sys.stderr)
            sys.exit(1)

    try:
        mid = resolve_marketplace_id(params, "getContentDocument")
        ids = _norm_str_list(params["includedDataSet"], "includedDataSet")
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    if not ids:
        print("includedDataSet must contain at least one value", file=sys.stderr)
        sys.exit(1)

    key = str(params["contentReferenceKey"]).strip()
    if not key:
        print("contentReferenceKey must be non-empty", file=sys.stderr)
        sys.exit(1)

    query_string = _build_query(mid, ids)
    path = f"{APLUS_PATH_PREFIX}/contentDocuments/{encode_path_segment(key)}"

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
    merge_success_json(out, proxy, "getContentDocumentResponse")
    inline = lf_inline_flag()
    emit_result(out, inline)


if __name__ == "__main__":
    main()
