"""Shopee Push module API registry (v2.push.*)."""

from __future__ import annotations

from typing import Literal, TypedDict


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
        "notes": '配置回调地址及推送设置；提交完整请求体。',
    },
    "get_app_push_config": {
        "path": "api/v2/push/get_app_push_config",
        "method": "GET",
        "response_key": "getAppPushConfig",
        "notes": '读取当前应用的推送配置。',
    },
    "get_lost_push_message": {
        "path": "api/v2/push/get_lost_push_message",
        "method": "GET",
        "response_key": "getLostPushMessage",
        "notes": '读取丢失消息，用于补推处理。',
    },
    "confirm_consumed_lost_push_message": {
        "path": "api/v2/push/confirm_consumed_lost_push_message",
        "method": "POST",
        "response_key": "confirmConsumedLostPushMessage",
        "notes": '确认已经处理的补推消息；提交完整请求体。',
    },
}

RESERVED_PARAM_KEYS = frozenset({
    "shopId", "merchantId", "skipDepCheck", "body", "requestBody", "api", "contentType",
})

LIST_QUERY_FIELDS = frozenset()


def list_api_names() -> list[str]:
    return sorted(PUSH_ENDPOINTS.keys())
