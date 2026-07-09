"""Shopee Push module API registry (v2.push.*)."""

from __future__ import annotations

from typing import Literal, TypedDict

SHOPEE_DOC_MODULE = "105"

class PushEndpoint(TypedDict, total=False):
    path: str
    method: Literal["GET", "POST"]
    response_key: str
    required: list[str]
    body_fields: list[str]
    notes: str

PUSH_ENDPOINTS: dict[str, PushEndpoint] = {
    "set_app_push_config": {
        "path": "api/v2/push/set_app_push_config",
        "method": "POST",
        "response_key": "setAppPushConfig",
        "notes": 'Configure app push callback URL and settings; pass full body',
    },
    "get_app_push_config": {
        "path": "api/v2/push/get_app_push_config",
        "method": "GET",
        "response_key": "getAppPushConfig",
        "notes": 'Get current app push configuration',
    },
    "get_lost_push_message": {
        "path": "api/v2/push/get_lost_push_message",
        "method": "GET",
        "response_key": "getLostPushMessage",
        "notes": 'Retrieve lost push messages for replay',
    },
    "confirm_consumed_lost_push_message": {
        "path": "api/v2/push/confirm_consumed_lost_push_message",
        "method": "POST",
        "response_key": "confirmConsumedLostPushMessage",
        "notes": 'Confirm consumed lost push messages; pass full body',
    },
}

RESERVED_PARAM_KEYS = frozenset({
    "shopId", "merchantId", "skipDepCheck", "body", "requestBody", "api", "contentType",
})

LIST_QUERY_FIELDS = frozenset()

def official_doc_url(api_name: str) -> str:
    return (
        f"https://open.shopee.com/documents/v2/v2.push.{api_name}"
        f"?module={SHOPEE_DOC_MODULE}&type=1"
    )

def list_api_names() -> list[str]:
    return sorted(PUSH_ENDPOINTS.keys())
