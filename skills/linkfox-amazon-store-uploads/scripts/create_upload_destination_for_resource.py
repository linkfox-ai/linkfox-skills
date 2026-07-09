#!/usr/bin/env python3
"""
Amazon Store — createUploadDestinationForResource (Uploads API v2020-11-01)
==========================================================================

POST `uploads/2020-11-01/uploadDestinations/{resource}`，获取上传 URL 与 headers，
供后续 `upload_to_destination.py` 将文件 PUT 到 Amazon。

官方参考: https://developer-docs.amazon.com/sp-api/reference/createuploaddestinationforresource

Usage:
  python create_upload_destination_for_resource.py '{
    "sellerId": "A1...",
    "region": "NA",
    "resource": "aplus/2020-11-01/contentDocuments",
    "marketplaceId": "ATVPDKIKX0DER",
    "filePath": "/path/to/image.jpg",
    "contentType": "image/jpeg"
  }'

也可直接传 contentMD5（Base64 MD5 摘要），与待上传字节一致。
"""

from __future__ import annotations

import json
import sys
from urllib.parse import quote

from _spapi_uploads_common import (
    developer_proxy_post,
    emit_result,
    ensure_auth_skill_available,
    get_store_tokens,
    lf_inline_flag,
    load_cli_params,
    merge_success_json,
    path_for_upload_destination,
    require_seller_region,
    resolve_content_md5,
    resolve_marketplace_id,
)


def _build_query(params: dict) -> str:
    mid = resolve_marketplace_id(params)
    md5 = resolve_content_md5(params)
    parts = [
        f"marketplaceIds={quote(mid, safe='')}",
        f"contentMD5={quote(md5, safe='')}",
    ]
    ct = params.get("contentType")
    if ct:
        parts.append(f"contentType={quote(str(ct).strip(), safe='')}")
    return "&".join(parts)


def main() -> None:
    params = load_cli_params()
    if not params:
        print(
            "Usage: create_upload_destination_for_resource.py '<JSON>'\n"
            "Required: sellerId, region, resource, marketplaceId, "
            "and contentMD5 OR filePath/content/contentBase64\n"
            "Optional: contentType",
            file=sys.stderr,
        )
        sys.exit(1)

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available("create_upload_destination_for_resource.py")

    if "resource" not in params:
        print("Missing required field: resource", file=sys.stderr)
        sys.exit(1)

    seller_id, region = require_seller_region(params)
    path = path_for_upload_destination(params["resource"])
    qs = _build_query(params)

    tokens = get_store_tokens(seller_id, region)
    if "error" in tokens or "accessToken" not in tokens:
        print(json.dumps(tokens, indent=2, ensure_ascii=False))
        sys.exit(1)

    proxy = developer_proxy_post(region, path, tokens["accessToken"], query_string=qs)
    out: dict = {
        "developerProxy": proxy,
        "resolvedPath": path,
        "queryString": qs,
        "resource": str(params["resource"]).strip(),
    }
    merge_success_json(out, proxy, "uploadDestination")
    inline = lf_inline_flag()
    emit_result(out, inline)


if __name__ == "__main__":
    main()
