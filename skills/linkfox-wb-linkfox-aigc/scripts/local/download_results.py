#!/usr/bin/env python3
"""Download media URLs from a successful AIGC taskQuery response."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen


def extract_urls(payload: object) -> list[str]:
    if isinstance(payload, list):
        values = payload
    elif isinstance(payload, dict):
        values = payload.get("resultList") or []
    else:
        raise ValueError("input must be a taskQuery object or an array")

    urls: list[str] = []
    for item in values:
        url = item.get("url") if isinstance(item, dict) else item
        if isinstance(url, str) and url:
            urls.append(url)
    return urls


def download(url: str, out_dir: Path, index: int) -> Path:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError(f"unsupported URL scheme: {parsed.scheme or '<empty>'}")
    name = Path(parsed.path).name or f"result-{index:02d}"
    target = out_dir / name
    if target.exists():
        stem, suffix = target.stem, target.suffix
        target = out_dir / f"{stem}-{index:02d}{suffix}"

    with urlopen(url, timeout=300) as response, target.open("wb") as output:
        while chunk := response.read(1024 * 1024):
            output.write(chunk)
    return target.resolve()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("response_file", help="JSON file containing resultList or a URL array")
    parser.add_argument("--out-dir", required=True, help="directory for downloaded media")
    args = parser.parse_args()

    with open(args.response_file, encoding="utf-8") as source:
        payload = json.load(source)
    urls = extract_urls(payload)
    if not urls:
        raise SystemExit("no media URLs found in resultList")

    out_dir = Path(os.path.abspath(args.out_dir))
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = [str(download(url, out_dir, index)) for index, url in enumerate(urls, 1)]
    print(json.dumps(paths, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
