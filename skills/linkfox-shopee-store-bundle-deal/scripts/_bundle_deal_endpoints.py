"""Shopee Bundle Deal module API registry (v2.bundle_deal.*)."""

from __future__ import annotations

from typing import Literal, TypedDict

SHOPEE_DOC_MODULE = "110"

class BundleDealEndpoint(TypedDict, total=False):
    path: str
    method: Literal["GET", "POST"]
    response_key: str
    required: list[str]
    body_fields: list[str]
    notes: str

BUNDLE_DEAL_ENDPOINTS: dict[str, BundleDealEndpoint] = {
    "add_bundle_deal": {
        "path": "api/v2/bundle_deal/add_bundle_deal",
        "method": "POST",
        "response_key": "addBundleDeal",
        "notes": 'Create bundle deal promotion; pass full body',
    },
    "add_bundle_deal_item": {
        "path": "api/v2/bundle_deal/add_bundle_deal_item",
        "method": "POST",
        "response_key": "addBundleDealItem",
        "notes": 'Add items to bundle deal',
    },
    "get_bundle_deal_list": {
        "path": "api/v2/bundle_deal/get_bundle_deal_list",
        "method": "GET",
        "response_key": "getBundleDealList",
        "notes": 'List bundle deals; pagination/status filters',
    },
    "get_bundle_deal": {
        "path": "api/v2/bundle_deal/get_bundle_deal",
        "method": "GET",
        "response_key": "getBundleDeal",
        "notes": 'Bundle deal detail by bundle_deal_id',
    },
    "get_bundle_deal_item": {
        "path": "api/v2/bundle_deal/get_bundle_deal_item",
        "method": "GET",
        "response_key": "getBundleDealItem",
        "notes": 'Items in bundle deal',
    },
    "update_bundle_deal": {
        "path": "api/v2/bundle_deal/update_bundle_deal",
        "method": "POST",
        "response_key": "updateBundleDeal",
        "notes": 'Update bundle deal settings',
    },
    "update_bundle_deal_item": {
        "path": "api/v2/bundle_deal/update_bundle_deal_item",
        "method": "POST",
        "response_key": "updateBundleDealItem",
        "notes": 'Update bundle deal item settings',
    },
    "end_bundle_deal": {
        "path": "api/v2/bundle_deal/end_bundle_deal",
        "method": "POST",
        "response_key": "endBundleDeal",
        "notes": 'End bundle deal early',
    },
    "delete_bundle_deal": {
        "path": "api/v2/bundle_deal/delete_bundle_deal",
        "method": "POST",
        "response_key": "deleteBundleDeal",
        "notes": 'Delete bundle deal',
    },
    "delete_bundle_deal_item": {
        "path": "api/v2/bundle_deal/delete_bundle_deal_item",
        "method": "POST",
        "response_key": "deleteBundleDealItem",
        "notes": 'Remove items from bundle deal',
    },
}

RESERVED_PARAM_KEYS = frozenset({
    "shopId", "merchantId", "skipDepCheck", "body", "requestBody", "api", "contentType",
})

LIST_QUERY_FIELDS = frozenset()

def official_doc_url(api_name: str) -> str:
    return (
        f"https://open.shopee.com/documents/v2/v2.bundle_deal.{api_name}"
        f"?module={SHOPEE_DOC_MODULE}&type=1"
    )

def list_api_names() -> list[str]:
    return sorted(BUNDLE_DEAL_ENDPOINTS.keys())
