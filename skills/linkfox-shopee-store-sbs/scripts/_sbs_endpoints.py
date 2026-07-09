"""Shopee SBS module API registry (v2.sbs.*)."""

from __future__ import annotations

from typing import Literal, TypedDict

SHOPEE_DOC_MODULE = "124"

class SbsEndpoint(TypedDict, total=False):
    path: str
    method: Literal["GET", "POST"]
    response_key: str
    required: list[str]
    body_fields: list[str]
    notes: str

SBS_ENDPOINTS: dict[str, SbsEndpoint] = {
    "get_bound_whs_info": {
        "path": "api/v2/sbs/get_bound_whs_info",
        "method": "GET",
        "response_key": "getBoundWhsInfo",
        "notes": 'Bound warehouse info for SBS',
    },
    "get_current_inventory": {
        "path": "api/v2/sbs/get_current_inventory",
        "method": "GET",
        "response_key": "getCurrentInventory",
        "notes": 'Current SBS inventory levels',
    },
    "get_expiry_report": {
        "path": "api/v2/sbs/get_expiry_report",
        "method": "GET",
        "response_key": "getExpiryReport",
        "notes": 'Inventory expiry report',
    },
    "get_stock_aging": {
        "path": "api/v2/sbs/get_stock_aging",
        "method": "GET",
        "response_key": "getStockAging",
        "notes": 'Stock aging report',
    },
    "get_stock_movement": {
        "path": "api/v2/sbs/get_stock_movement",
        "method": "GET",
        "response_key": "getStockMovement",
        "notes": 'Stock movement history',
    },
}

RESERVED_PARAM_KEYS = frozenset({
    "shopId", "merchantId", "skipDepCheck", "body", "requestBody", "api", "contentType",
})

LIST_QUERY_FIELDS = frozenset()

def official_doc_url(api_name: str) -> str:
    return (
        f"https://open.shopee.com/documents/v2/v2.sbs.{api_name}"
        f"?module={SHOPEE_DOC_MODULE}&type=1"
    )

def list_api_names() -> list[str]:
    return sorted(SBS_ENDPOINTS.keys())
