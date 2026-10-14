#!/usr/bin/env python3
"""Upload a local image to an already-issued presigned PUT URL."""

import json
import ipaddress
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, urlunsplit
from urllib.request import Request, urlopen


CONTENT_TYPE_MAP = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "gif": "image/gif",
    "webp": "image/webp",
    "heic": "image/heic",
}


def validate_presigned_url(value: str) -> str:
    parts = urlsplit(value)
    if parts.scheme != "https" or not parts.netloc or not parts.query:
        raise ValueError("presigned_url must be an absolute HTTPS URL with a signature query")
    if parts.username is not None or parts.password is not None:
        raise ValueError("presigned_url must not contain userinfo")

    hostname = (parts.hostname or "").rstrip(".").lower()
    if not hostname:
        raise ValueError("presigned_url must contain a hostname")
    try:
        hostname = hostname.encode("idna").decode("ascii")
        parts.port
    except (UnicodeError, ValueError) as exc:
        raise ValueError("presigned_url contains an invalid hostname or port") from exc

    if hostname == "localhost" or hostname.endswith(".localhost"):
        raise ValueError("presigned_url must not target localhost")
    if (
        hostname == "tool-gateway.linkfox.com"
        or hostname.endswith(".tool-gateway.linkfox.com")
        or hostname == "mcp-tool-gateway.linkfox.com"
        or hostname.endswith(".mcp-tool-gateway.linkfox.com")
    ):
        raise ValueError("presigned_url must not target a LinkFox tool gateway")

    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        address = None
    if address is not None and not address.is_global:
        raise ValueError("presigned_url must not target a non-public IP address")
    return value


def get_content_type(file_path: str) -> str:
    if not os.path.isfile(file_path):
        raise ValueError(f"File not found: {file_path}")
    extension = os.path.splitext(file_path)[1].lstrip(".").lower()
    content_type = CONTENT_TYPE_MAP.get(extension)
    if not content_type:
        supported = ", ".join(CONTENT_TYPE_MAP)
        raise ValueError(f"Unsupported image format: .{extension}; supported: {supported}")
    return content_type


def upload_file(presigned_url: str, file_path: str, content_type: str) -> None:
    with open(file_path, "rb") as handle:
        file_data = handle.read()
    request = Request(
        presigned_url,
        data=file_data,
        headers={"Content-Type": content_type, "x-oss-object-acl": "public-read"},
        method="PUT",
    )
    try:
        with urlopen(request, timeout=120) as response:
            if response.status not in (200, 201):
                raise RuntimeError(f"Upload failed with status: {response.status}")
    except HTTPError as exc:
        raise RuntimeError(f"Upload failed: HTTP {exc.code}: {exc.reason}") from exc
    except URLError as exc:
        raise RuntimeError(f"Upload connection failed: {exc.reason}") from exc


def public_url(presigned_url: str) -> str:
    parts = urlsplit(presigned_url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: upload_image.py <local_image_path>", file=sys.stderr)
        return 2
    try:
        file_path = sys.argv[1]
        content_type = get_content_type(file_path)
        presigned_url = validate_presigned_url(sys.stdin.readline().strip())
        upload_file(presigned_url, file_path, content_type)
    except (ValueError, RuntimeError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps({"url": public_url(presigned_url), "contentType": content_type}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
