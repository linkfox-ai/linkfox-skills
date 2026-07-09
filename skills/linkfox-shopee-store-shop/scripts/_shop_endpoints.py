"""Shopee Shop module API registry (v2.shop.*)."""

from __future__ import annotations

from typing import Literal, TypedDict

SHOPEE_DOC_MODULE = "92"


class ShopEndpoint(TypedDict, total=False):
    path: str
    method: Literal["GET", "POST"]
    response_key: str
    required: list[str]
    body_fields: list[str]
    notes: str


SHOP_ENDPOINTS: dict[str, ShopEndpoint] = {
    "get_shop_info": {
        "path": "api/v2/shop/get_shop_info",
        "method": "GET",
        "response_key": "getShopInfo",
        "notes": "Region, status, auth/expire time, merchant_id, fulfillment flags",
    },
    "get_profile": {
        "path": "api/v2/shop/get_profile",
        "method": "GET",
        "response_key": "getProfile",
        "notes": "shop_name, shop_logo, description; BR may include invoice_issuer",
    },
    "update_profile": {
        "path": "api/v2/shop/update_profile",
        "method": "POST",
        "response_key": "updateProfile",
        "body_fields": ["shop_name", "shop_logo", "description"],
        "notes": "At least one body field; shop_name change limited to once per 30 days",
    },
    "get_warehouse_detail": {
        "path": "api/v2/shop/get_warehouse_detail",
        "method": "GET",
        "response_key": "getWarehouseDetail",
        "notes": "Optional query warehouse_type: 1=pickup (default), 2=return",
    },
    "get_shop_notification": {
        "path": "api/v2/shop/get_shop_notification",
        "method": "GET",
        "response_key": "getShopNotification",
        "notes": "Optional cursor, page_size (default 10, max 50)",
    },
    "get_authorised_reseller_brand": {
        "path": "api/v2/shop/get_authorised_reseller_brand",
        "method": "GET",
        "response_key": "getAuthorisedResellerBrand",
        "required": ["page_no", "page_size"],
        "notes": "page_size min 1 max 30",
    },
    "get_br_shop_onboarding_info": {
        "path": "api/v2/shop/get_br_shop_onboarding_info",
        "method": "GET",
        "response_key": "getBrShopOnboardingInfo",
        "notes": "Brazil shop only — KYC / tax onboarding",
    },
    "get_shop_holiday_mode": {
        "path": "api/v2/shop/get_shop_holiday_mode",
        "method": "GET",
        "response_key": "getShopHolidayMode",
        "notes": "Returns holiday_mode_on and holiday_mode_mtime",
    },
    "set_shop_holiday_mode": {
        "path": "api/v2/shop/set_shop_holiday_mode",
        "method": "POST",
        "response_key": "setShopHolidayMode",
        "required": ["holiday_mode_on"],
        "body_fields": ["holiday_mode_on"],
        "notes": "true=enable holiday mode (blocks new orders)",
    },
}

RESERVED_PARAM_KEYS = frozenset({
    "shopId",
    "merchantId",
    "skipDepCheck",
    "body",
    "requestBody",
    "api",
    "contentType",
})


def official_doc_url(api_name: str) -> str:
    return (
        f"https://open.shopee.com/documents/v2/v2.shop.{api_name}"
        f"?module={SHOPEE_DOC_MODULE}&type=1"
    )


def list_api_names() -> list[str]:
    return sorted(SHOP_ENDPOINTS.keys())
