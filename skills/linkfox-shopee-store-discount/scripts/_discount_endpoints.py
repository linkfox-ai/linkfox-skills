"""Shopee Discount module API registry (v2.discount.*)."""

from __future__ import annotations

from typing import Literal, TypedDict

SHOPEE_DOC_MODULE = "99"

class DiscountEndpoint(TypedDict, total=False):
    path: str
    method: Literal["GET", "POST"]
    response_key: str
    required: list[str]
    body_fields: list[str]
    notes: str

DISCOUNT_ENDPOINTS: dict[str, DiscountEndpoint] = {
    "add_discount": {
        "path": "api/v2/discount/add_discount",
        "method": "POST",
        "response_key": "addDiscount",
        "notes": 'Create discount promotion; pass full body',
    },
    "add_discount_item": {
        "path": "api/v2/discount/add_discount_item",
        "method": "POST",
        "response_key": "addDiscountItem",
        "notes": 'Add items to discount; pass body',
    },
    "delete_discount": {
        "path": "api/v2/discount/delete_discount",
        "method": "POST",
        "response_key": "deleteDiscount",
        "notes": 'Delete discount; pass body with discount_id',
    },
    "delete_discount_item": {
        "path": "api/v2/discount/delete_discount_item",
        "method": "POST",
        "response_key": "deleteDiscountItem",
        "notes": 'Remove items from discount',
    },
    "get_discount": {
        "path": "api/v2/discount/get_discount",
        "method": "GET",
        "response_key": "getDiscount",
        "notes": 'Get discount detail by discount_id',
    },
    "get_discount_list": {
        "path": "api/v2/discount/get_discount_list",
        "method": "GET",
        "response_key": "getDiscountList",
        "notes": 'List discounts; pagination/status filters',
    },
    "update_discount": {
        "path": "api/v2/discount/update_discount",
        "method": "POST",
        "response_key": "updateDiscount",
        "notes": 'Update discount settings',
    },
    "update_discount_item": {
        "path": "api/v2/discount/update_discount_item",
        "method": "POST",
        "response_key": "updateDiscountItem",
        "notes": 'Update discount item settings',
    },
    "end_discount": {
        "path": "api/v2/discount/end_discount",
        "method": "POST",
        "response_key": "endDiscount",
        "notes": 'End discount early',
    },
    "get_sip_discounts": {
        "path": "api/v2/discount/get_sip_discounts",
        "method": "GET",
        "response_key": "getSipDiscounts",
        "notes": 'SIP cross-border discount list',
    },
    "set_sip_discount": {
        "path": "api/v2/discount/set_sip_discount",
        "method": "POST",
        "response_key": "setSipDiscount",
        "notes": 'Set SIP discount',
    },
    "delete_sip_discount": {
        "path": "api/v2/discount/delete_sip_discount",
        "method": "POST",
        "response_key": "deleteSipDiscount",
        "notes": 'Delete SIP discount',
    },
}

RESERVED_PARAM_KEYS = frozenset({
    "shopId", "merchantId", "skipDepCheck", "body", "requestBody", "api", "contentType",
})

LIST_QUERY_FIELDS = frozenset()

def official_doc_url(api_name: str) -> str:
    return (
        f"https://open.shopee.com/documents/v2/v2.discount.{api_name}"
        f"?module={SHOPEE_DOC_MODULE}&type=1"
    )

def list_api_names() -> list[str]:
    return sorted(DISCOUNT_ENDPOINTS.keys())
