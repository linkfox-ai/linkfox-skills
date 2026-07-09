"""Shopee Follow Prize module API registry (v2.follow_prize.*)."""

from __future__ import annotations

from typing import Literal, TypedDict

SHOPEE_DOC_MODULE = "113"

class FollowPrizeEndpoint(TypedDict, total=False):
    path: str
    method: Literal["GET", "POST"]
    response_key: str
    required: list[str]
    body_fields: list[str]
    notes: str

FOLLOW_PRIZE_ENDPOINTS: dict[str, FollowPrizeEndpoint] = {
    "add_follow_prize": {
        "path": "api/v2/follow_prize/add_follow_prize",
        "method": "POST",
        "response_key": "addFollowPrize",
        "notes": 'Create follow prize promotion; pass full body',
    },
    "delete_follow_prize": {
        "path": "api/v2/follow_prize/delete_follow_prize",
        "method": "POST",
        "response_key": "deleteFollowPrize",
        "notes": 'Delete follow prize',
    },
    "end_follow_prize": {
        "path": "api/v2/follow_prize/end_follow_prize",
        "method": "POST",
        "response_key": "endFollowPrize",
        "notes": 'End follow prize early',
    },
    "update_follow_prize": {
        "path": "api/v2/follow_prize/update_follow_prize",
        "method": "POST",
        "response_key": "updateFollowPrize",
        "notes": 'Update follow prize settings',
    },
    "get_follow_prize_detail": {
        "path": "api/v2/follow_prize/get_follow_prize_detail",
        "method": "GET",
        "response_key": "getFollowPrizeDetail",
        "notes": 'Follow prize detail by campaign_id',
    },
    "get_follow_prize_list": {
        "path": "api/v2/follow_prize/get_follow_prize_list",
        "method": "GET",
        "response_key": "getFollowPrizeList",
        "notes": 'List follow prizes; pagination/status filters',
    },
}

RESERVED_PARAM_KEYS = frozenset({
    "shopId", "merchantId", "skipDepCheck", "body", "requestBody", "api", "contentType",
})

LIST_QUERY_FIELDS = frozenset()

def official_doc_url(api_name: str) -> str:
    return (
        f"https://open.shopee.com/documents/v2/v2.follow_prize.{api_name}"
        f"?module={SHOPEE_DOC_MODULE}&type=1"
    )

def list_api_names() -> list[str]:
    return sorted(FOLLOW_PRIZE_ENDPOINTS.keys())
