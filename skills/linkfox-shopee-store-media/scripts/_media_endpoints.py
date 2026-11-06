"""Shopee Media module API registry (v2.media.*)."""

from __future__ import annotations

from typing import Literal, TypedDict


class MediaEndpoint(TypedDict, total=False):
    path: str
    method: Literal["GET", "POST"]
    response_key: str
    required: list[str]
    body_fields: list[str]
    notes: str

MEDIA_ENDPOINTS: dict[str, MediaEndpoint] = {
    "upload_image": {
        "path": "api/v2/media/upload_image",
        "method": "POST",
        "response_key": "uploadImage",
        "notes": 'Upload image; returns Shopee image URL',
    },
    "init_video_upload": {
        "path": "api/v2/media/init_video_upload",
        "method": "POST",
        "response_key": "initVideoUpload",
        "notes": 'Init chunked video upload session; pass body',
    },
    "upload_video_part": {
        "path": "api/v2/media/upload_video_part",
        "method": "POST",
        "response_key": "uploadVideoPart",
        "notes": 'Upload video chunk; pass body via developerProxy',
    },
    "complete_video_upload": {
        "path": "api/v2/media/complete_video_upload",
        "method": "POST",
        "response_key": "completeVideoUpload",
        "notes": 'Complete video upload after all parts sent',
    },
    "get_video_upload_result": {
        "path": "api/v2/media/get_video_upload_result",
        "method": "GET",
        "response_key": "getVideoUploadResult",
        "notes": 'Query video upload result/status',
    },
    "cancel_video_upload": {
        "path": "api/v2/media/cancel_video_upload",
        "method": "POST",
        "response_key": "cancelVideoUpload",
        "notes": 'Cancel in-progress video upload',
    },
}

RESERVED_PARAM_KEYS = frozenset({
    "shopId", "merchantId", "skipDepCheck", "body", "requestBody", "api", "contentType", "accessToken",
})

LIST_QUERY_FIELDS = frozenset()


def list_api_names() -> list[str]:
    return sorted(MEDIA_ENDPOINTS.keys())
