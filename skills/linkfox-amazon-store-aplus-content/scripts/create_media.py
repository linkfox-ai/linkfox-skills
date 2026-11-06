#!/usr/bin/env python3
"""Create an A+ media asset or video-thumbnail pairing through the LinkFox proxy."""

from __future__ import annotations

import json
import sys

from _spapi_aplus_common import APLUS_PATH_PREFIX, ensure_auth_skill_available, run_proxy


def _require_text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value


def _validate_reference(media: dict, field: str) -> None:
    identifiers = [key for key in ("uploadDestinationId", "mediaId") if key in media]
    if len(identifiers) != 1:
        raise ValueError(f"{field} requires exactly one of uploadDestinationId or mediaId")
    key = identifiers[0]
    _require_text(media[key], f"{field}.{key}")


def _validate_media_request(media: object) -> dict:
    if not isinstance(media, dict):
        raise ValueError("mediaRequest must be a JSON object")
    media_type = media.get("mediaType")
    if media_type not in ("IMAGE", "VIDEO"):
        raise ValueError("mediaRequest.mediaType must be IMAGE or VIDEO")
    _validate_reference(media, "mediaRequest")
    if media_type == "IMAGE":
        if "descriptions" in media:
            raise ValueError("descriptions are not valid for IMAGE media")
        if "title" in media:
            _require_text(media["title"], "mediaRequest.title")
        return media

    descriptions = media.get("descriptions")
    if not isinstance(descriptions, list) or not descriptions:
        raise ValueError("VIDEO media requires a non-empty descriptions array")
    locales = set()
    for description in descriptions:
        if not isinstance(description, dict):
            raise ValueError("each description must be an object with locale and value")
        locale = _require_text(description.get("locale"), "description.locale")
        _require_text(description.get("value"), "description.value")
        if locale in locales:
            raise ValueError("descriptions must not contain duplicate locales")
        locales.add(locale)

    pairings = media.get("relatedMedia")
    if not isinstance(pairings, list) or len(pairings) != 1:
        raise ValueError("VIDEO media requires exactly one relatedMedia entry")
    pairing = pairings[0]
    if not isinstance(pairing, dict) or pairing.get("associationType") != "VIDEO_PAIRING":
        raise ValueError("relatedMedia entry must have associationType VIDEO_PAIRING")
    title = _require_text(pairing.get("title"), "relatedMedia.title")
    if len(title.split()) < 3 or title.isupper():
        raise ValueError("VIDEO_PAIRING title must contain at least three words and not be all uppercase")
    thumbnail = pairing.get("media")
    if not isinstance(thumbnail, dict) or thumbnail.get("mediaType") != "IMAGE":
        raise ValueError("VIDEO_PAIRING media must be an IMAGE object")
    _validate_reference(thumbnail, "relatedMedia.media")
    return media


def _valid_media_result(result: object, request: dict) -> bool:
    if not isinstance(result, dict):
        return False
    media_id = result.get("mediaId")
    statuses = result.get("status")
    if not isinstance(media_id, str) or not media_id.strip():
        return False
    if result.get("mediaType") != request["mediaType"]:
        return False
    if not isinstance(result.get("title"), str):
        return False
    if not isinstance(statuses, list):
        return False
    if not all(isinstance(status, str) and status.strip() for status in statuses):
        return False
    return "mediaId" not in request or media_id == request["mediaId"]


def main() -> None:
    if len(sys.argv) < 2 or "--help" in sys.argv[1:]:
        print(
            "Usage: create_media.py '<JSON>' [--inline] [--no-cache]\n"
            "Required: sellerId, region, mediaRequest (object)\n"
            "Optional: skipDepCheck",
            file=sys.stdout if "--help" in sys.argv[1:] else sys.stderr,
        )
        if len(sys.argv) < 2:
            raise SystemExit(1)
        return
    try:
        params = json.loads(sys.argv[1])
        if not isinstance(params, dict):
            raise ValueError("JSON parameters must be an object")
        seller_id = _require_text(params.get("sellerId"), "sellerId").strip()
        region = _require_text(params.get("region"), "region").strip().upper()
        if region not in ("NA", "EU", "FE"):
            raise ValueError("region must be NA, EU or FE")
        if "skipDepCheck" in params and not isinstance(params["skipDepCheck"], bool):
            raise ValueError("skipDepCheck must be a boolean")
        media = _validate_media_request(params.get("mediaRequest"))
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available("create_media.py")
    run_proxy(
        "createMedia", "POST", region, f"{APLUS_PATH_PREFIX}/media", seller_id, "",
        result_field="createMediaResponse", body_obj=media, success_http=(200, 201),
        result_validator=lambda result: _valid_media_result(result, media),
    )


if __name__ == "__main__":
    main()
