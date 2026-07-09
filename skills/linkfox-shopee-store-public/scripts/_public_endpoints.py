"""Shopee Public module API registry (v2.public.*)."""

from __future__ import annotations

from typing import Literal, TypedDict

SHOPEE_DOC_MODULE = "104"

class PublicEndpoint(TypedDict, total=False):
    path: str
    method: Literal["GET", "POST"]
    response_key: str
    required: list[str]
    body_fields: list[str]
    notes: str

PUBLIC_ENDPOINTS: dict[str, PublicEndpoint] = {
    "get_shops_by_partner": {
        "path": "api/v2/public/get_shops_by_partner",
        "method": "GET",
        "response_key": "getShopsByPartner",
        "notes": 'List shops authorized to partner',
    },
    "get_merchants_by_partner": {
        "path": "api/v2/public/get_merchants_by_partner",
        "method": "GET",
        "response_key": "getMerchantsByPartner",
        "notes": 'List merchants authorized to partner',
    },
    "get_access_token": {
        "path": "api/v2/public/get_access_token",
        "method": "POST",
        "response_key": "getAccessToken",
        "notes": 'Exchange auth code for access token; pass full body',
    },
    "refresh_access_token": {
        "path": "api/v2/public/refresh_access_token",
        "method": "POST",
        "response_key": "refreshAccessToken",
        "notes": 'Refresh access token; pass full body',
    },
    "get_token_by_resend_code": {
        "path": "api/v2/public/get_token_by_resend_code",
        "method": "POST",
        "response_key": "getTokenByResendCode",
        "notes": 'Get token by resend code; pass full body',
    },
    "get_shopee_ip_ranges": {
        "path": "api/v2/public/get_shopee_ip_ranges",
        "method": "GET",
        "response_key": "getShopeeIpRanges",
        "notes": 'Shopee Open Platform IP ranges for allowlisting',
    },
}

RESERVED_PARAM_KEYS = frozenset({
    "shopId", "merchantId", "skipDepCheck", "body", "requestBody", "api", "contentType",
})

LIST_QUERY_FIELDS = frozenset()

def official_doc_url(api_name: str) -> str:
    return (
        f"https://open.shopee.com/documents/v2/v2.public.{api_name}"
        f"?module={SHOPEE_DOC_MODULE}&type=1"
    )

def list_api_names() -> list[str]:
    return sorted(PUBLIC_ENDPOINTS.keys())
