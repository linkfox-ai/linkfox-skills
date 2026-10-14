#!/usr/bin/env python3
"""Inspect a local image or upload it to an already-issued presigned URL."""

from __future__ import annotations

import json
import mimetypes
import sys
from pathlib import Path
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


def inspect_image(file_path: str) -> dict[str, str]:
    path = Path(file_path).expanduser()
    if not path.is_file():
        raise ValueError(f"File not found: {path}")

    extension = path.suffix.lstrip(".").lower()
    content_type = CONTENT_TYPE_MAP.get(extension)
    if not content_type:
        supported = ", ".join(sorted(CONTENT_TYPE_MAP))
        raise ValueError(f"Unsupported image format: .{extension}; supported: {supported}")

    guessed = mimetypes.guess_type(path.name)[0]
    if guessed and guessed != content_type:
        raise ValueError(f"Image extension and MIME type disagree: {path.name}")

    return {
        "contentType": content_type,
        "fileExtension": extension,
    }


def public_url(presigned_url: str) -> str:
    parsed = urlsplit(presigned_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("presignedUrl must be an absolute HTTP(S) URL")
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", ""))


def upload_file(presigned_url: str, file_path: str) -> dict[str, str]:
    metadata = inspect_image(file_path)
    path = Path(file_path).expanduser()
    url = public_url(presigned_url)
    request = Request(
        presigned_url,
        data=path.read_bytes(),
        headers={
            "Content-Type": metadata["contentType"],
            "x-oss-object-acl": "public-read",
        },
        method="PUT",
    )
    try:
        with urlopen(request, timeout=120) as response:
            if response.status not in (200, 201):
                raise RuntimeError(f"Upload failed with status {response.status}")
    except HTTPError as exc:
        raise RuntimeError(f"Upload failed with HTTP {exc.code}: {exc.reason}") from exc
    except URLError as exc:
        raise RuntimeError(f"Upload connection failed: {exc.reason}") from exc

    return {"url": url, **metadata}


def main() -> None:
    if len(sys.argv) < 3 or sys.argv[1] not in {"inspect", "put"}:
        print(
            "Usage:\n"
            "  upload_image.py inspect <local_image_path>\n"
            "  upload_image.py put <presigned_url> <local_image_path>",
            file=sys.stderr,
        )
        raise SystemExit(2)

    try:
        if sys.argv[1] == "inspect" and len(sys.argv) == 3:
            result = inspect_image(sys.argv[2])
        elif sys.argv[1] == "put" and len(sys.argv) == 4:
            result = upload_file(sys.argv[2], sys.argv[3])
        else:
            raise ValueError("invalid argument count")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
