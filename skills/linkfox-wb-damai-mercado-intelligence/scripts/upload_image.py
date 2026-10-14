#!/usr/bin/env python3
"""Upload one local image to a presigned OSS URL supplied on stdin."""

import json
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


def public_url(presigned_url: str) -> str:
    parts = urlsplit(presigned_url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def upload_file(presigned_url: str, file_path: str, content_type: str) -> None:
    with open(file_path, "rb") as image_file:
        request = Request(
            presigned_url,
            data=image_file.read(),
            headers={
                "Content-Type": content_type,
                "x-oss-object-acl": "public-read",
            },
            method="PUT",
        )
    try:
        with urlopen(request, timeout=150) as response:
            if response.status not in (200, 201):
                raise RuntimeError(f"upload returned HTTP {response.status}")
    except HTTPError as exc:
        raise RuntimeError(f"upload returned HTTP {exc.code}") from exc
    except URLError as exc:
        raise RuntimeError(f"upload connection failed: {exc.reason}") from exc


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: upload_image.py <local_image_path>", file=sys.stderr)
        return 2

    file_path = sys.argv[1]
    if not os.path.isfile(file_path):
        print(f"File not found: {file_path}", file=sys.stderr)
        return 2

    extension = os.path.splitext(file_path)[1].lstrip(".").lower()
    content_type = CONTENT_TYPE_MAP.get(extension)
    if content_type is None:
        print(
            f"Unsupported image format: .{extension}; supported: "
            + ", ".join(CONTENT_TYPE_MAP),
            file=sys.stderr,
        )
        return 2

    presigned_url = sys.stdin.readline().strip()
    parsed = urlsplit(presigned_url)
    if parsed.scheme != "https" or not parsed.netloc or not parsed.query:
        print("A valid HTTPS presigned URL with a query string is required on stdin.", file=sys.stderr)
        return 2

    try:
        upload_file(presigned_url, file_path, content_type)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(
        json.dumps(
            {"url": public_url(presigned_url), "contentType": content_type},
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
