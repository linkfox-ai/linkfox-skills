#!/usr/bin/env python3
"""
Amazon Store — Upload feed document contents (post createFeedDocument)
======================================================================

createFeedDocument 返回的 **url** 需用 **PUT** 上传 feed 文件内容（不经 developerProxy）。
本脚本使用标准库直接请求 Amazon 预签名 URL。

Usage:
  python upload_feed_document.py '{
    "uploadUrl": "https://...",
    "contentType": "text/tab-separated-values; charset=UTF-8",
    "filePath": "/path/to/feed.tsv"
  }'

或：
  "content": "<raw string>"  /  "contentBase64": "<base64>"
"""

from __future__ import annotations

import base64
import json
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from _spapi_feeds_common import emit_result, lf_inline_flag


def _load_bytes(params: dict) -> bytes:
    if params.get("filePath"):
        p = Path(str(params["filePath"]).expanduser())
        if not p.is_file():
            print(f"filePath not found: {p}", file=sys.stderr)
            sys.exit(1)
        return p.read_bytes()
    if params.get("contentBase64"):
        try:
            return base64.b64decode(str(params["contentBase64"]))
        except Exception as e:
            print(f"Invalid contentBase64: {e}", file=sys.stderr)
            sys.exit(1)
    if "content" in params:
        raw = params["content"]
        if isinstance(raw, str):
            return raw.encode("utf-8")
        print("content must be a string", file=sys.stderr)
        sys.exit(1)
    print("Provide one of: filePath, content, contentBase64", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: upload_feed_document.py '<JSON>'\n"
            "Required: uploadUrl, contentType, and filePath | content | contentBase64",
            file=sys.stderr,
        )
        sys.exit(1)
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    for f in ("uploadUrl", "contentType"):
        if f not in params:
            print(f"Missing required field: {f}", file=sys.stderr)
            sys.exit(1)

    upload_url = str(params["uploadUrl"]).strip()
    content_type = str(params["contentType"]).strip()
    payload = _load_bytes(params)

    req = Request(
        upload_url,
        data=payload,
        headers={"Content-Type": content_type},
        method="PUT",
    )
    out: dict = {"uploadUrl": upload_url, "bytesUploaded": len(payload)}
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
