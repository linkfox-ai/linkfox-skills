#!/usr/bin/env python3
"""
Amazon Store — postContentDocumentApprovalSubmission (SP-API A+ Content Management v2020-11-01)

提交 A+ 文档供审核、批准与发布。

官方参考: https://developer-docs.amazon.com/sp-api/reference/postcontentdocumentapprovalsubmission

Usage:
  python post_content_document_approval_submission.py '{"sellerId":"A1...","region":"NA","marketplaceId":"ATVPDKIKX0DER","contentReferenceKey":"..."}'
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
            "Usage: post_content_document_approval_submission.py '<JSON>'\n"
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

    if not isinstance(params, dict):
        print("JSON parameters must be an object", file=sys.stderr)
        sys.exit(1)

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available("post_content_document_approval_submission.py")

    for f in ("sellerId", "region", "contentReferenceKey"):
        if f not in params:
            print(f"Missing required field: {f}", file=sys.stderr)
            sys.exit(1)

    try:
        mid = resolve_marketplace_id(params, "postContentDocumentApprovalSubmission")
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    key = str(params["contentReferenceKey"]).strip()
    if not key:
        print("contentReferenceKey must be non-empty", file=sys.stderr)
        sys.exit(1)

    query_string = f"marketplaceId={quote(mid, safe='')}"
    path = (
        f"{APLUS_PATH_PREFIX}/contentDocuments/{encode_path_segment(key)}/approvalSubmissions"
    )

    seller_id = str(params["sellerId"])
    region = str(params["region"])

    run_proxy("postContentDocumentApprovalSubmission", "POST", region, path, seller_id,
              query_string, result_field="postContentDocumentApprovalSubmissionResponse")


if __name__ == "__main__":
    main()
