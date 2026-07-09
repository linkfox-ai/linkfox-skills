#!/usr/bin/env python3
"""
Amazon Store — PUT file to createUploadDestinationForResource URL
=================================================================

在调用 create_upload_destination_for_resource 之后，将文件上传到返回的 **url**，
并附带响应中的 **headers**（不经 developerProxy）。

Usage:
  python upload_to_destination.py '{
    "uploadUrl": "https://...",
    "headers": { "Content-Type": "image/jpeg", "Content-MD5": "..." },
    "filePath": "/path/to/image.jpg"
  }'

也可传 uploadDestination 对象（含 url、headers）：
  "uploadDestination": { "url": "...", "headers": { ... } }
"""

from __future__ import annotations

import json
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from _spapi_uploads_common import emit_result, lf_inline_flag, load_cli_params, load_file_bytes


def _resolve_upload_target(params: dict) -> tuple[str, dict]:
    dest = params.get("uploadDestination")
    if isinstance(dest, dict):
        url = dest.get("url") or params.get("uploadUrl")
        headers = dest.get("headers") or params.get("headers") or {}
    else:
        url = params.get("uploadUrl")
        headers = params.get("headers") or {}
    if not url:
        print("Missing uploadUrl or uploadDestination.url", file=sys.stderr)
        sys.exit(1)
    if not isinstance(headers, dict):
        print("headers must be a JSON object", file=sys.stderr)
        sys.exit(1)
    return str(url).strip(), {str(k): str(v) for k, v in headers.items()}


def main() -> None:
    params = load_cli_params()
    if not params:
        print(
            "Usage: upload_to_destination.py '<JSON>'\n"
            "Required: uploadUrl (or uploadDestination), headers, "
            "and filePath | content | contentBase64",
            file=sys.stderr,
        )
        sys.exit(1)

    upload_url, hdrs = _resolve_upload_target(params)
    payload = load_file_bytes(params)
    if not payload:
        print("Provide filePath, content, or contentBase64", file=sys.stderr)
        sys.exit(1)

    req = Request(upload_url, data=payload, headers=hdrs, method="PUT")
    out: dict = {
        "uploadUrl": upload_url,
        "bytesUploaded": len(payload),
        "requestHeaders": hdrs,
    }
    try:
        with urlopen(req, timeout=300) as resp:
            out["httpStatus"] = resp.status
            out["success"] = 200 <= resp.status < 300
    except HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        out["httpStatus"] = e.code
        out["success"] = False
        out["error"] = f"HTTP {e.code}: {e.reason}"
        out["details"] = body[:2000]
    except URLError as e:
        out["success"] = False
        out["error"] = f"Connection failed: {e.reason}"

    inline = lf_inline_flag()
    emit_result(out, inline)
    if not out.get("success"):
        sys.exit(1)


if __name__ == "__main__":
    main()
