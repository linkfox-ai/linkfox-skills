"""Shopee Merchant module API registry (v2.merchant.*)."""

from __future__ import annotations

from typing import Literal, TypedDict

SHOPEE_DOC_MODULE = "93"

class MerchantEndpoint(TypedDict, total=False):
    path: str
    method: Literal["GET", "POST"]
    response_key: str
    required: list[str]
    body_fields: list[str]
    notes: str

MERCHANT_ENDPOINTS: dict[str, MerchantEndpoint] = {
    "get_merchant_info": {
        "path": "api/v2/merchant/get_merchant_info",
        "method": "GET",
        "response_key": "getMerchantInfo",
        "notes": 'Merchant name, region, currency, auth/expire time',
    },
    "get_shop_list_by_merchant": {
        "path": "api/v2/merchant/get_shop_list_by_merchant",
        "method": "GET",
        "response_key": "getShopListByMerchant",
        "required": ['page_no', 'page_size'],
        "notes": 'Shops bound to merchant; page_size max 500',
    },
    "get_merchant_warehouse_location_list": {
        "path": "api/v2/merchant/get_merchant_warehouse_location_list",
        "method": "GET",
        "response_key": "getMerchantWarehouseLocationList",
        "notes": 'Merchant warehouse locations',
    },
    "get_merchant_warehouse_list": {
        "path": "api/v2/merchant/get_merchant_warehouse_list",
        "method": "GET",
        "response_key": "getMerchantWarehouseList",
        "notes": 'Merchant warehouse list',
    },
    "get_warehouse_eligible_shop_list": {
        "path": "api/v2/merchant/get_warehouse_eligible_shop_list",
        "method": "GET",
        "response_key": "getWarehouseEligibleShopList",
        "notes": 'Shops eligible for warehouse',
    },
    "get_merchant_prepaid_account_list": {
        "path": "api/v2/merchant/get_merchant_prepaid_account_list",
        "method": "GET",
        "response_key": "getMerchantPrepaidAccountList",
        "notes": 'Merchant prepaid accounts',
    },
}

RESERVED_PARAM_KEYS = frozenset({
    "shopId", "merchantId", "skipDepCheck", "body", "requestBody", "api", "contentType",
})

LIST_QUERY_FIELDS = frozenset()

def official_doc_url(api_name: str) -> str:
    return (
        f"https://open.shopee.com/documents/v2/v2.merchant.{api_name}"
        f"?module={SHOPEE_DOC_MODULE}&type=1"
    )

def list_api_names() -> list[str]:
    return sorted(MERCHANT_ENDPOINTS.keys())
