#!/usr/bin/env python3
"""
Amazon Store — createUploadDestinationForResource (Uploads API v2020-11-01)
==========================================================================

POST `uploads/2020-11-01/uploadDestinations/{resource}`，获取上传 URL 与 headers，
供后续 `upload_to_destination.py` 按目的地使用 PUT 或 multipart POST 上传到 Amazon。

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
    ensure_auth_skill_available,
    load_cli_params,
    merge_success_json,
    path_for_upload_destination,
    require_seller_region,
    resolve_content_md5,
    resolve_marketplace_id,
    load_file_bytes,
    content_md5_base64,
    is_normal_response,
    resolve_upload_destination,
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
            "Optional: contentType, uploadFile (boolean), uploadMethod (PUT/POST)",
            file=sys.stderr,
        )
        sys.exit(1)

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available("create_upload_destination_for_resource.py")

    if "resource" not in params:
        print("Missing required field: resource", file=sys.stderr)
        sys.exit(1)

    resource = str(params["resource"]).strip().lstrip("/")
    if resource.startswith("aplus/") and not str(params.get("contentType") or "").strip():
        print("contentType is required for A+ uploads", file=sys.stderr)
        sys.exit(1)
    upload_requested = params.get("uploadFile", False)
    if not isinstance(upload_requested, bool):
        print("uploadFile must be a boolean", file=sys.stderr)
        sys.exit(1)
    payload = None
    upload_method = str(params.get("uploadMethod") or ("POST" if resource.startswith("aplus/") else "PUT")).strip().upper()
    if upload_requested:
        if upload_method not in ("PUT", "POST"):
            print("uploadMethod must be PUT or POST", file=sys.stderr)
            sys.exit(1)
        payload = load_file_bytes(params)
        if not payload:
            print("uploadFile requires non-empty filePath, contentBase64 or content", file=sys.stderr)
            sys.exit(1)
        digest = content_md5_base64(payload)
        if params.get("contentMD5") and str(params["contentMD5"]).strip() != digest:
            print("contentMD5 does not match the supplied file bytes", file=sys.stderr)
            sys.exit(1)
        params = {**params, "contentMD5": digest}

    seller_id, region = require_seller_region(params)
    path = path_for_upload_destination(params["resource"])
    qs = _build_query(params)

    transport_status = None
    def build_result(status, proxy):
        nonlocal transport_status
        transport_status = status
        out = {
            "developerProxy": proxy,
            "transportHttpStatus": status,
            "resolvedPath": path,
            "queryString": qs,
            "resource": str(params["resource"]).strip(),
        }
        if isinstance(proxy, dict):
            merge_success_json(out, proxy, "uploadDestination", transport_status=status)
            resolved = resolve_upload_destination(out.get("uploadDestination"))
            if isinstance(resolved, dict):
                out["resolvedUploadDestination"] = resolved
        return out

    proxy = developer_proxy_post(region, path, seller_id, query_string=qs, result_builder=build_result)
    if upload_requested:
        if not is_normal_response(transport_status, proxy) or proxy.get("httpStatus") not in (200, 201):
            print("Upload destination creation failed; file upload was not started", file=sys.stderr)
            sys.exit(1)
        raw = proxy.get("body")
        try:
            destination = resolve_upload_destination(json.loads(raw) if isinstance(raw, str) else raw)
        except (TypeError, ValueError):
            destination = None
        if not isinstance(destination, dict) or not destination.get("url"):
            print("Upload destination response is missing a usable url", file=sys.stderr)
            sys.exit(1)
        from upload_to_destination import upload_file
        upload_file({**params, "uploadDestination": destination, "method": upload_method}, payload=payload)



if __name__ == "__main__":
    main()
