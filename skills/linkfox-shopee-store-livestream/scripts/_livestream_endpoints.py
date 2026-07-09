"""Shopee Livestream module API registry (v2.livestream.*)."""

from __future__ import annotations

from typing import Literal, TypedDict

SHOPEE_DOC_MODULE = "125"

class LivestreamEndpoint(TypedDict, total=False):
    path: str
    method: Literal["GET", "POST"]
    response_key: str
    required: list[str]
    body_fields: list[str]
    notes: str

LIVESTREAM_ENDPOINTS: dict[str, LivestreamEndpoint] = {
    "upload_image": {
        "path": "api/v2/livestream/upload_image",
        "method": "POST",
        "response_key": "uploadImage",
        "notes": 'Upload livestream image',
    },
    "create_session": {
        "path": "api/v2/livestream/create_session",
        "method": "POST",
        "response_key": "createSession",
        "notes": 'Create livestream session; pass full body',
    },
    "update_session": {
        "path": "api/v2/livestream/update_session",
        "method": "POST",
        "response_key": "updateSession",
        "notes": 'Update livestream session',
    },
    "start_session": {
        "path": "api/v2/livestream/start_session",
        "method": "POST",
        "response_key": "startSession",
        "notes": 'Start livestream session',
    },
    "end_session": {
        "path": "api/v2/livestream/end_session",
        "method": "POST",
        "response_key": "endSession",
        "notes": 'End livestream session',
    },
    "get_session_detail": {
        "path": "api/v2/livestream/get_session_detail",
        "method": "GET",
        "response_key": "getSessionDetail",
        "notes": 'Livestream session detail',
    },
    "add_item_list": {
        "path": "api/v2/livestream/add_item_list",
        "method": "POST",
        "response_key": "addItemList",
        "notes": 'Add items to livestream',
    },
    "delete_item_list": {
        "path": "api/v2/livestream/delete_item_list",
        "method": "POST",
        "response_key": "deleteItemList",
        "notes": 'Remove items from livestream',
    },
    "update_item_list": {
        "path": "api/v2/livestream/update_item_list",
        "method": "POST",
        "response_key": "updateItemList",
        "notes": 'Update livestream item list',
    },
    "get_item_count": {
        "path": "api/v2/livestream/get_item_count",
        "method": "GET",
        "response_key": "getItemCount",
        "notes": 'Livestream item count',
    },
    "get_item_list": {
        "path": "api/v2/livestream/get_item_list",
        "method": "GET",
        "response_key": "getItemList",
        "notes": 'Livestream item list',
    },
    "update_show_item": {
        "path": "api/v2/livestream/update_show_item",
        "method": "POST",
        "response_key": "updateShowItem",
        "notes": 'Update currently shown item',
    },
    "delete_show_item": {
        "path": "api/v2/livestream/delete_show_item",
        "method": "POST",
        "response_key": "deleteShowItem",
        "notes": 'Remove currently shown item',
    },
    "get_show_item": {
        "path": "api/v2/livestream/get_show_item",
        "method": "GET",
        "response_key": "getShowItem",
        "notes": 'Get currently shown item',
    },
    "get_like_item_list": {
        "path": "api/v2/livestream/get_like_item_list",
        "method": "GET",
        "response_key": "getLikeItemList",
        "notes": 'Liked items in livestream',
    },
    "get_recent_item_list": {
        "path": "api/v2/livestream/get_recent_item_list",
        "method": "GET",
        "response_key": "getRecentItemList",
        "notes": 'Recently shown items',
    },
    "get_item_set_list": {
        "path": "api/v2/livestream/get_item_set_list",
        "method": "GET",
        "response_key": "getItemSetList",
        "notes": 'Livestream item set list',
    },
    "get_item_set_item_list": {
        "path": "api/v2/livestream/get_item_set_item_list",
        "method": "GET",
        "response_key": "getItemSetItemList",
        "notes": 'Items in item set',
    },
    "apply_item_set": {
        "path": "api/v2/livestream/apply_item_set",
        "method": "POST",
        "response_key": "applyItemSet",
        "notes": 'Apply item set to session',
    },
    "get_session_metric": {
        "path": "api/v2/livestream/get_session_metric",
        "method": "GET",
        "response_key": "getSessionMetric",
        "notes": 'Livestream session metrics',
    },
    "get_session_item_metric": {
        "path": "api/v2/livestream/get_session_item_metric",
        "method": "GET",
        "response_key": "getSessionItemMetric",
        "notes": 'Livestream item metrics',
    },
    "get_latest_comment_list": {
        "path": "api/v2/livestream/get_latest_comment_list",
        "method": "GET",
        "response_key": "getLatestCommentList",
        "notes": 'Latest comments in livestream',
    },
    "post_comment": {
        "path": "api/v2/livestream/post_comment",
        "method": "POST",
        "response_key": "postComment",
        "notes": 'Post comment in livestream',
    },
    "ban_user_comment": {
        "path": "api/v2/livestream/ban_user_comment",
        "method": "POST",
        "response_key": "banUserComment",
        "notes": 'Ban user from commenting',
    },
    "unban_user_comment": {
        "path": "api/v2/livestream/unban_user_comment",
        "method": "POST",
        "response_key": "unbanUserComment",
        "notes": 'Unban user from commenting',
    },
}

RESERVED_PARAM_KEYS = frozenset({
    "shopId", "merchantId", "skipDepCheck", "body", "requestBody", "api", "contentType",
})

LIST_QUERY_FIELDS = frozenset()

def official_doc_url(api_name: str) -> str:
    return (
        f"https://open.shopee.com/documents/v2/v2.livestream.{api_name}"
        f"?module={SHOPEE_DOC_MODULE}&type=1"
    )

def list_api_names() -> list[str]:
    return sorted(LIVESTREAM_ENDPOINTS.keys())
