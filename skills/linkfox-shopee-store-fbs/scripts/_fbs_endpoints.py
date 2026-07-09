"""Shopee FBS module API registry (v2.fbs.*)."""

from __future__ import annotations

from typing import Literal, TypedDict

SHOPEE_DOC_MODULE = "126"

class FbsEndpoint(TypedDict, total=False):
    path: str
    method: Literal["GET", "POST"]
    response_key: str
    required: list[str]
    body_fields: list[str]
    notes: str

FBS_ENDPOINTS: dict[str, FbsEndpoint] = {
    "query_br_shop_enrollment_status": {
        "path": "api/v2/fbs/query_br_shop_enrollment_status",
        "method": "GET",
        "response_key": "queryBrShopEnrollmentStatus",
        "notes": 'Brazil FBS shop enrollment status',
    },
    "query_br_shop_invoice_error": {
        "path": "api/v2/fbs/query_br_shop_invoice_error",
        "method": "GET",
        "response_key": "queryBrShopInvoiceError",
        "notes": 'Brazil FBS shop invoice errors',
    },
    "query_br_shop_block_status": {
        "path": "api/v2/fbs/query_br_shop_block_status",
        "method": "GET",
        "response_key": "queryBrShopBlockStatus",
        "notes": 'Brazil FBS shop block status',
    },
    "query_br_sku_block_status": {
        "path": "api/v2/fbs/query_br_sku_block_status",
        "method": "GET",
        "response_key": "queryBrSkuBlockStatus",
        "notes": 'Brazil FBS SKU block status',
    },
}

RESERVED_PARAM_KEYS = frozenset({
    "shopId", "merchantId", "skipDepCheck", "body", "requestBody", "api", "contentType",
})

LIST_QUERY_FIELDS = frozenset()

def official_doc_url(api_name: str) -> str:
    return (
        f"https://open.shopee.com/documents/v2/v2.fbs.{api_name}"
        f"?module={SHOPEE_DOC_MODULE}&type=1"
    )

def list_api_names() -> list[str]:
    return sorted(FBS_ENDPOINTS.keys())
