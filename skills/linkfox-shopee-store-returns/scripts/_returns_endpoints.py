"""Shopee Returns module API registry (v2.returns.*)."""

from __future__ import annotations

from typing import Literal, TypedDict

SHOPEE_DOC_MODULE = "102"

class ReturnsEndpoint(TypedDict, total=False):
    path: str
    method: Literal["GET", "POST"]
    response_key: str
    required: list[str]
    body_fields: list[str]
    notes: str

RETURNS_ENDPOINTS: dict[str, ReturnsEndpoint] = {
    "get_return_list": {
        "path": "api/v2/returns/get_return_list",
        "method": "GET",
        "response_key": "getReturnList",
        "notes": 'Return/refund list; optional page_no, page_size, create_time_from/to',
    },
    "get_return_detail": {
        "path": "api/v2/returns/get_return_detail",
        "method": "GET",
        "response_key": "getReturnDetail",
        "required": ['return_sn'],
        "notes": 'Return detail by return_sn',
    },
    "confirm": {
        "path": "api/v2/returns/confirm",
        "method": "POST",
        "response_key": "confirm",
        "notes": 'Seller confirm return; pass body with return_sn',
    },
    "dispute": {
        "path": "api/v2/returns/dispute",
        "method": "POST",
        "response_key": "dispute",
        "notes": 'Open return dispute; pass full body',
    },
    "get_available_solutions": {
        "path": "api/v2/returns/get_available_solutions",
        "method": "GET",
        "response_key": "getAvailableSolutions",
        "required": ['return_sn'],
        "notes": 'Available solutions for return',
    },
    "offer": {
        "path": "api/v2/returns/offer",
        "method": "POST",
        "response_key": "offer",
        "notes": 'Seller offer solution; pass full body',
    },
    "accept_offer": {
        "path": "api/v2/returns/accept_offer",
        "method": "POST",
        "response_key": "acceptOffer",
        "notes": 'Accept buyer/seller offer; pass full body',
    },
    "convert_image": {
        "path": "api/v2/returns/convert_image",
        "method": "POST",
        "response_key": "convertImage",
        "notes": 'Convert image for return proof',
    },
    "upload_proof": {
        "path": "api/v2/returns/upload_proof",
        "method": "POST",
        "response_key": "uploadProof",
        "notes": 'Upload return proof; pass full body',
    },
    "query_proof": {
        "path": "api/v2/returns/query_proof",
        "method": "GET",
        "response_key": "queryProof",
        "notes": 'Query uploaded proof',
    },
    "get_return_dispute_reason": {
        "path": "api/v2/returns/get_return_dispute_reason",
        "method": "GET",
        "response_key": "getReturnDisputeReason",
        "notes": 'Dispute reason list',
    },
    "cancel_dispute": {
        "path": "api/v2/returns/cancel_dispute",
        "method": "POST",
        "response_key": "cancelDispute",
        "notes": 'Cancel dispute; pass body with return_sn',
    },
    "get_shipping_carrier": {
        "path": "api/v2/returns/get_shipping_carrier",
        "method": "GET",
        "response_key": "getShippingCarrier",
        "notes": 'Return shipping carriers',
    },
    "upload_shipping_proof": {
        "path": "api/v2/returns/upload_shipping_proof",
        "method": "POST",
        "response_key": "uploadShippingProof",
        "notes": 'Upload return shipping proof',
    },
    "get_reverse_tracking_info": {
        "path": "api/v2/returns/get_reverse_tracking_info",
        "method": "GET",
        "response_key": "getReverseTrackingInfo",
        "notes": 'Reverse logistics tracking; return_sn etc.',
    },
}

RESERVED_PARAM_KEYS = frozenset({
    "shopId", "merchantId", "skipDepCheck", "body", "requestBody", "api", "contentType",
})

LIST_QUERY_FIELDS = frozenset()

def official_doc_url(api_name: str) -> str:
    return (
        f"https://open.shopee.com/documents/v2/v2.returns.{api_name}"
        f"?module={SHOPEE_DOC_MODULE}&type=1"
    )

def list_api_names() -> list[str]:
    return sorted(RETURNS_ENDPOINTS.keys())
