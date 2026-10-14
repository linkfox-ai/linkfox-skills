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
import base64
import ipaddress
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


def _validate_upload_url(value: str) -> str:
    parsed = urlsplit(value)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("upload URL must be an absolute HTTPS URL without userinfo")
    hostname = parsed.hostname.lower()
    if hostname == "localhost" or hostname.endswith(".localhost"):
        raise ValueError("upload URL must not target localhost")
    if hostname == "tool-gateway.linkfox.com" or hostname.endswith(".tool-gateway.linkfox.com"):
        raise ValueError("upload URL must not target the LinkFox tool gateway")
    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        pass
    else:
        if not address.is_global:
            raise ValueError("upload URL must not target a non-public IP address")
    return value

def load_cli_params() -> dict:
    if len(sys.argv) < 2:
        return {}
    try:
        value = json.loads(sys.argv[1])
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON: {exc}", file=sys.stderr)
        sys.exit(1)
    return value if isinstance(value, dict) else {}


def load_file_bytes(params: dict) -> bytes:
    if params.get("filePath"):
        path = Path(str(params["filePath"])).expanduser()
        if not path.is_file():
            print(f"filePath not found: {path}", file=sys.stderr)
            sys.exit(1)
        return path.read_bytes()
    if params.get("contentBase64"):
        try:
            return base64.b64decode(str(params["contentBase64"]), validate=True)
        except ValueError as exc:
            print(f"Invalid contentBase64: {exc}", file=sys.stderr)
            sys.exit(1)
    if isinstance(params.get("content"), str):
        return params["content"].encode("utf-8")
    return b""


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
    try:
        upload_url = _validate_upload_url(str(url).strip())
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
    return upload_url, {str(k): str(v) for k, v in headers.items()}


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
        "bytesUploaded": len(payload),
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

    print(json.dumps(out, ensure_ascii=False))
    if not out.get("success"):
        sys.exit(1)


if __name__ == "__main__":
    main()
