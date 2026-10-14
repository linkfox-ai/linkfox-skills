#!/usr/bin/env python3
"""Upload a local file sequentially to a trusted file-gateway upload URL."""

from __future__ import annotations

import argparse
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


MIN_CHUNK = 5 * 1024 * 1024
MAX_CHUNK = 64 * 1024 * 1024
MAX_CHUNKS = 1000


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--upload-url", required=True, help="Complete HTTPS URL returned by Initialize")
    parser.add_argument("--file", required=True, dest="file_path")
    parser.add_argument("--chunk-size", type=int, default=10 * 1024 * 1024)
    parser.add_argument("--content-type", default="video/mp4")
    parser.add_argument("--dry-run", action="store_true", help="Validate and print chunk ranges without network access")
    return parser.parse_args()


def validate(args: argparse.Namespace) -> tuple[str, int, int]:
    parsed = urllib.parse.urlsplit(args.upload_url)
    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError("upload URL must be an absolute HTTPS URL")
    hostname = parsed.hostname.lower()
    if hostname == "tool-gateway.linkfox.com" or hostname.endswith(".tool-gateway.linkfox.com"):
        raise ValueError("tool-gateway URLs are forbidden; use the file-gateway URL returned by Initialize")
    file_path = os.path.abspath(args.file_path)
    if not os.path.isfile(file_path):
        raise ValueError(f"file does not exist: {file_path}")
    if args.chunk_size < MIN_CHUNK or args.chunk_size > MAX_CHUNK:
        raise ValueError("chunk size must be between 5 MiB and 64 MiB")
    total = os.path.getsize(file_path)
    if total <= 0:
        raise ValueError("file must not be empty")
    chunks = (total + args.chunk_size - 1) // args.chunk_size
    if chunks > MAX_CHUNKS:
        raise ValueError("chunk count exceeds 1000; increase --chunk-size")
    return file_path, total, chunks


def upload(args: argparse.Namespace, file_path: str, total: int, chunks: int) -> None:
    with open(file_path, "rb") as source:
        for index in range(chunks):
            first = index * args.chunk_size
            payload = source.read(min(args.chunk_size, total - first))
            last = first + len(payload) - 1
            print(f"chunk {index + 1}/{chunks}: bytes {first}-{last}/{total}")
            if args.dry_run:
                continue
            request = urllib.request.Request(
                args.upload_url,
                data=payload,
                method="PUT",
                headers={
                    "Content-Type": args.content_type,
                    "Content-Length": str(len(payload)),
                    "Content-Range": f"bytes {first}-{last}/{total}",
                },
            )
            try:
                with urllib.request.urlopen(request, timeout=300) as response:
                    if not 200 <= response.status < 300:
                        raise RuntimeError(f"chunk {index + 1} returned HTTP {response.status}")
            except urllib.error.HTTPError as exc:
                raise RuntimeError(f"chunk {index + 1} returned HTTP {exc.code}") from exc
            except urllib.error.URLError as exc:
                raise RuntimeError(f"chunk {index + 1} transport failed: {exc.reason}") from exc


def main() -> int:
    args = parse_args()
    try:
        file_path, total, chunks = validate(args)
        upload(args, file_path, total, chunks)
    except (ValueError, OSError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
