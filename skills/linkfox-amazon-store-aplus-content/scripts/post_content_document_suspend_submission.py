#!/usr/bin/env python3
"""
Amazon Store — postContentDocumentSuspendSubmission (SP-API A+ Content Management v2020-11-01)

请求暂停 A+ 在详情页的可见展示；**不会**删除文档本体或 ASIN 关联。

官方参考: https://developer-docs.amazon.com/sp-api/reference/postcontentdocumentsuspendsubmission

Usage:
  python post_content_document_suspend_submission.py '{"sellerId":"A1...","region":"NA","marketplaceId":"ATVPDKIKX0DER","contentReferenceKey":"..."}'
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


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: post_content_document_suspend_submission.py '<JSON>'\n"
            "Required: sellerId, region, marketplaceId (or marketplaceIds), contentReferenceKey\n"
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
        ensure_auth_skill_available("post_content_document_suspend_submission.py")

    for f in ("sellerId", "region", "contentReferenceKey"):
        if f not in params:
            print(f"Missing required field: {f}", file=sys.stderr)
            sys.exit(1)

    try:
        mid = resolve_marketplace_id(params, "postContentDocumentSuspendSubmission")
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    key = str(params["contentReferenceKey"]).strip()
    if not key:
        print("contentReferenceKey must be non-empty", file=sys.stderr)
        sys.exit(1)

    query_string = f"marketplaceId={quote(mid, safe='')}"
    path = (
        f"{APLUS_PATH_PREFIX}/contentDocuments/{encode_path_segment(key)}/suspendSubmissions"
    )

    seller_id = str(params["sellerId"])
    region = str(params["region"])

    tokens = get_store_tokens(seller_id, region)
    if "error" in tokens or "accessToken" not in tokens:
        print(json.dumps(tokens, indent=2, ensure_ascii=False))
        sys.exit(1)

    proxy = developer_proxy_post(
        region, path, tokens["accessToken"], query_string=query_string, body_obj=None
    )
    out: dict = {
        "developerProxy": proxy,
        "resolvedPath": path,
        "queryString": query_string,
    }
    merge_success_json(out, proxy, "postContentDocumentSuspendSubmissionResponse")
    inline = lf_inline_flag()
    emit_result(out, inline)


if __name__ == "__main__":
    main()
