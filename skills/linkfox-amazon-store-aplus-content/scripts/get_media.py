#!/usr/bin/env python3
"""Retrieve an A+ media asset, processing status and video-thumbnail pairing."""

from __future__ import annotations

import json
import sys
from urllib.parse import quote

from _spapi_aplus_common import (
    APLUS_PATH_PREFIX,
    encode_path_segment,
    ensure_auth_skill_available,
    run_proxy,
)


def _require_text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value.strip()


def _valid_media_result(result: object, media_id: str) -> bool:
    if not isinstance(result, dict) or result.get("mediaId") != media_id:
        return False
    if result.get("mediaType") not in ("IMAGE", "VIDEO"):
        return False
    if not isinstance(result.get("title"), str):
        return False
    statuses = result.get("status")
    return (
        isinstance(statuses, list)
        and all(isinstance(status, str) and status.strip() for status in statuses)
    )


def main() -> None:
    if len(sys.argv) < 2 or "--help" in sys.argv[1:]:
        print(
            "Usage: get_media.py '<JSON>' [--inline] [--no-cache]\n"
            "Required: sellerId, region, mediaId\n"
            "Optional: associatedMediaId, skipDepCheck",
            file=sys.stdout if "--help" in sys.argv[1:] else sys.stderr,
        )
        if len(sys.argv) < 2:
            raise SystemExit(1)
        return
    try:
        params = json.loads(sys.argv[1])
        if not isinstance(params, dict):
            raise ValueError("JSON parameters must be an object")
        seller_id = _require_text(params.get("sellerId"), "sellerId")
        region = _require_text(params.get("region"), "region").upper()
        if region not in ("NA", "EU", "FE"):
            raise ValueError("region must be NA, EU or FE")
        media_id = _require_text(params.get("mediaId"), "mediaId")
        query_string = ""
        if "associatedMediaId" in params:
            associated_id = _require_text(params["associatedMediaId"], "associatedMediaId")
            query_string = f"associatedMediaId={quote(associated_id, safe='')}"
        if "skipDepCheck" in params and not isinstance(params["skipDepCheck"], bool):
            raise ValueError("skipDepCheck must be a boolean")
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available("get_media.py")
    run_proxy(
        "getMedia", "GET", region,
        f"{APLUS_PATH_PREFIX}/media/{encode_path_segment(media_id)}",
        seller_id, query_string, result_field="getMediaResponse", success_http=(200,),
        result_validator=lambda result: _valid_media_result(result, media_id),
    )


if __name__ == "__main__":
    main()
