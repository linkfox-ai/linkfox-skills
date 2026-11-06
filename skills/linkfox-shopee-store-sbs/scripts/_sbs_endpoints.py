"""Shopee SBS module API registry (v2.sbs.*)."""

from __future__ import annotations

from typing import Literal, TypedDict


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


def list_api_names() -> list[str]:
    return sorted(SBS_ENDPOINTS.keys())
