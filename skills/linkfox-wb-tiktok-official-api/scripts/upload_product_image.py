#!/usr/bin/env python3
"""Build proxy_call arguments for a local TikTok Shop product image."""

from __future__ import annotations

import base64
import json
import mimetypes
import sys
from pathlib import Path
from urllib.parse import urlencode

MAX_IMAGE_BYTES = 10 * 1024 * 1024


def build_arguments(params: dict) -> dict:
    required = ("openId", "shop_cipher", "imagePath")
    missing = [key for key in required if not str(params.get(key, "")).strip()]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    image_path = Path(str(params["imagePath"])).expanduser()
    if not image_path.is_file():
        raise ValueError(f"Image file not found: {image_path}")
    raw = image_path.read_bytes()
    if len(raw) > MAX_IMAGE_BYTES:
        raise ValueError("Image exceeds TikTok's 10MB limit")

    content_type = str(
        params.get("contentType")
        or mimetypes.guess_type(image_path.name)[0]
        or "application/octet-stream"
    )
    return {
        "appType": "erp",
        "openId": str(params["openId"]).strip(),
        "path": "product/202309/images/upload",
        "method": "POST",
        "queryString": urlencode({"shop_cipher": str(params["shop_cipher"]).strip()}),
        "contentType": content_type,
        "multipartFileName": image_path.name,
        "multipartFileBase64": base64.b64encode(raw).decode("ascii"),
        "useCase": str(params.get("useCase") or "MAIN_IMAGE"),
    }


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: upload_product_image.py '<JSON parameters>'", file=sys.stderr)
        raise SystemExit(2)
    try:
        params = json.loads(sys.argv[1])
        if not isinstance(params, dict):
            raise ValueError("parameters must be a JSON object")
        print(json.dumps(build_arguments(params), ensure_ascii=False, indent=2))
    except (json.JSONDecodeError, ValueError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
