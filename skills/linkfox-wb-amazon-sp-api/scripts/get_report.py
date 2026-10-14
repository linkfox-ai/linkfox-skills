#!/usr/bin/env python3
"""Download and optionally decompress a report from a returned presigned URL."""

from __future__ import annotations

import gzip
import ipaddress
import json
import shutil
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


def _validate_download_url(value: str) -> str:
    parsed = urlsplit(value)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("downloadUrl must be an absolute HTTPS URL without userinfo")
    hostname = parsed.hostname.lower()
    if hostname == "localhost" or hostname.endswith(".localhost"):
        raise ValueError("downloadUrl must not target localhost")
    if hostname == "tool-gateway.linkfox.com" or hostname.endswith(".tool-gateway.linkfox.com"):
        raise ValueError("downloadUrl must not target the LinkFox tool gateway")
    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        pass
    else:
        if not address.is_global:
            raise ValueError("downloadUrl must not target a non-public IP address")
    return value


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: get_report.py '<JSON>'", file=sys.stderr)
        print("Required: downloadUrl, outputPath; optional: compressionAlgorithm", file=sys.stderr)
        raise SystemExit(1)
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON: {exc}", file=sys.stderr)
        raise SystemExit(1)
    url_value = str(params.get("downloadUrl") or "").strip()
    output_value = str(params.get("outputPath") or "").strip()
    if not url_value or not output_value:
        print("downloadUrl and outputPath are required", file=sys.stderr)
        raise SystemExit(1)
    try:
        url = _validate_download_url(url_value)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
    output = Path(output_value).expanduser()
    output.parent.mkdir(parents=True, exist_ok=True)
    raw_path = output.with_suffix(output.suffix + ".gz") if str(params.get("compressionAlgorithm", "")).upper() == "GZIP" else output
    try:
        with urlopen(Request(url, method="GET"), timeout=300) as response, raw_path.open("wb") as stream:
            shutil.copyfileobj(response, stream)
            status = response.status
        if raw_path != output:
            with gzip.open(raw_path, "rb") as source, output.open("wb") as destination:
                shutil.copyfileobj(source, destination)
            raw_path.unlink()
        print(json.dumps({"success": True, "httpStatus": status, "outputPath": str(output), "bytes": output.stat().st_size}, ensure_ascii=False))
    except (HTTPError, URLError, OSError) as exc:
        print(json.dumps({"success": False, "error": str(exc)}, ensure_ascii=False))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
