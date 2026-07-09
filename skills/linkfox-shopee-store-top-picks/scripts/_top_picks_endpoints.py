"""Shopee Top Picks module API registry (v2.top_picks.*)."""

from __future__ import annotations

from typing import Literal, TypedDict

SHOPEE_DOC_MODULE = "100"

class TopPicksEndpoint(TypedDict, total=False):
    path: str
    method: Literal["GET", "POST"]
    response_key: str
    required: list[str]
    body_fields: list[str]
    notes: str

TOP_PICKS_ENDPOINTS: dict[str, TopPicksEndpoint] = {
    "get_top_picks_list": {
        "path": "api/v2/top_picks/get_top_picks_list",
        "method": "GET",
        "response_key": "getTopPicksList",
        "notes": 'List top picks collections; pagination filters',
    },
    "add_top_picks": {
        "path": "api/v2/top_picks/add_top_picks",
        "method": "POST",
        "response_key": "addTopPicks",
        "notes": 'Create top picks collection; pass full body',
    },
    "update_top_picks": {
        "path": "api/v2/top_picks/update_top_picks",
        "method": "POST",
        "response_key": "updateTopPicks",
        "notes": 'Update top picks collection',
    },
    "delete_top_picks": {
        "path": "api/v2/top_picks/delete_top_picks",
        "method": "POST",
        "response_key": "deleteTopPicks",
        "notes": 'Delete top picks collection',
    },
}

RESERVED_PARAM_KEYS = frozenset({
    "shopId", "merchantId", "skipDepCheck", "body", "requestBody", "api", "contentType",
})

LIST_QUERY_FIELDS = frozenset()

def official_doc_url(api_name: str) -> str:
    return (
        f"https://open.shopee.com/documents/v2/v2.top_picks.{api_name}"
        f"?module={SHOPEE_DOC_MODULE}&type=1"
    )

def list_api_names() -> list[str]:
    return sorted(TOP_PICKS_ENDPOINTS.keys())
