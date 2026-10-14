#!/usr/bin/env python3
"""Upload a local image to an OSS URL already obtained through proxy_call.

This helper never contacts the LinkFox tool gateway. The agent must first call
proxy_call with toolName oss/file/presignedPut and pass the returned URL via
--presigned-url.
"""

import argparse
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


CONTENT_TYPE_MAP = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Upload a local image using an OSS presigned PUT URL."
    )
    parser.add_argument("image_path", help="Path to the local image")
    parser.add_argument(
        "--presigned-url",
        required=True,
        help="URL returned by proxy_call toolName oss/file/presignedPut",
    )
    return parser.parse_args()


def validate_presigned_url(url: str) -> None:
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("presigned URL must be an absolute HTTPS URL")
    if parsed.hostname and parsed.hostname.lower().endswith("tool-gateway.linkfox.com"):
        raise ValueError("refusing to upload directly to the LinkFox tool gateway")


def image_content_type(file_path: str) -> str:
    if not os.path.isfile(file_path):
        raise ValueError(f"file not found: {file_path}")
    extension = os.path.splitext(file_path)[1].lstrip(".").lower()
    content_type = CONTENT_TYPE_MAP.get(extension)
    if not content_type:
        supported = ", ".join(CONTENT_TYPE_MAP)
        raise ValueError(f"unsupported image format: .{extension}; supported: {supported}")
    return content_type


def upload_file(presigned_url: str, file_path: str, content_type: str) -> None:
    with open(file_path, "rb") as file_handle:
        payload = file_handle.read()

    request = Request(
        presigned_url,
        data=payload,
        headers={
            "Content-Type": content_type,
            "x-oss-object-acl": "public-read",
        },
        method="PUT",
    )
    try:
        with urlopen(request, timeout=120) as response:
            if response.status not in (200, 201):
                raise RuntimeError(f"OSS upload failed with status {response.status}")
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        raise RuntimeError(f"OSS upload failed: HTTP {exc.code}: {body[:300]}") from exc
    except URLError as exc:
        raise RuntimeError(f"OSS upload connection failed: {exc.reason}") from exc


def public_url(presigned_url: str) -> str:
    parsed = urlsplit(presigned_url)
    return parsed._replace(query="", fragment="").geturl()


def main() -> int:
    args = parse_args()
    try:
        validate_presigned_url(args.presigned_url)
        content_type = image_content_type(args.image_path)
        upload_file(args.presigned_url, args.image_path, content_type)
    except (ValueError, RuntimeError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps({"url": public_url(args.presigned_url)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
