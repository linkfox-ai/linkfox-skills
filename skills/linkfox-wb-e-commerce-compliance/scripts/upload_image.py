#!/usr/bin/env python3
"""Upload a local image to a presigned object-storage URL returned by MCP."""

import json
import mimetypes
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ALLOWED_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/heic",
}


def parse_args(raw: str) -> tuple[str, str, str]:
    try:
        params = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON: {exc}") from exc
    if not isinstance(params, dict):
        raise ValueError("Arguments must be a JSON object")
    presigned_url = params.get("presignedUrl")
    file_path = params.get("filePath")
    if not isinstance(presigned_url, str) or not presigned_url.startswith("https://"):
        raise ValueError("presignedUrl must be the HTTPS URL returned by oss/file/presignedPut")
    if not isinstance(file_path, str) or not os.path.isfile(file_path):
        raise ValueError("filePath must point to an existing local image")
    content_type = params.get("contentType") or mimetypes.guess_type(file_path)[0]
    if content_type not in ALLOWED_TYPES:
        raise ValueError(f"Unsupported contentType: {content_type}")
    return presigned_url, file_path, content_type


def upload(presigned_url: str, file_path: str, content_type: str) -> int:
    with open(file_path, "rb") as image:
        request = Request(
            presigned_url,
            data=image.read(),
            headers={"Content-Type": content_type, "x-oss-object-acl": "public-read"},
            method="PUT",
        )
    with urlopen(request, timeout=120) as response:
        return response.status


def main() -> int:
    if len(sys.argv) != 2:
        print(
            "Usage: upload_image.py '<JSON>'\n"
            "Required: presignedUrl, filePath; optional: contentType",
            file=sys.stderr,
        )
        return 2
    try:
        presigned_url, file_path, content_type = parse_args(sys.argv[1])
        status = upload(presigned_url, file_path, content_type)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except HTTPError as exc:
        print(f"Upload failed: HTTP {exc.code}: {exc.reason}", file=sys.stderr)
        return 1
    except URLError as exc:
        print(f"Upload connection failed: {exc.reason}", file=sys.stderr)
        return 1
    if status not in (200, 201):
        print(f"Upload failed with status: {status}", file=sys.stderr)
        return 1
    print(json.dumps({"url": presigned_url.split("?", 1)[0], "status": status}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
