"""Shopee Shop Category module API registry (v2.shop_category.*)."""

from __future__ import annotations

from typing import Literal, TypedDict

SHOPEE_DOC_MODULE = "101"

class ShopCategoryEndpoint(TypedDict, total=False):
    path: str
    method: Literal["GET", "POST"]
    response_key: str
    required: list[str]
    body_fields: list[str]
    notes: str

SHOP_CATEGORY_ENDPOINTS: dict[str, ShopCategoryEndpoint] = {
    "add_shop_category": {
        "path": "api/v2/shop_category/add_shop_category",
        "method": "POST",
        "response_key": "addShopCategory",
        "notes": 'Create shop category; pass full body',
    },
    "get_shop_category_list": {
        "path": "api/v2/shop_category/get_shop_category_list",
        "method": "GET",
        "response_key": "getShopCategoryList",
        "notes": 'List shop categories',
    },
    "delete_shop_category": {
        "path": "api/v2/shop_category/delete_shop_category",
        "method": "POST",
        "response_key": "deleteShopCategory",
        "notes": 'Delete shop category',
    },
    "update_shop_category": {
        "path": "api/v2/shop_category/update_shop_category",
        "method": "POST",
        "response_key": "updateShopCategory",
        "notes": 'Update shop category settings',
    },
    "add_item_list": {
        "path": "api/v2/shop_category/add_item_list",
        "method": "POST",
        "response_key": "addItemList",
        "notes": 'Add items to shop category',
    },
    "get_item_list": {
        "path": "api/v2/shop_category/get_item_list",
        "method": "GET",
        "response_key": "getItemList",
        "notes": 'Get items in shop category',
    },
    "delete_item_list": {
        "path": "api/v2/shop_category/delete_item_list",
        "method": "POST",
        "response_key": "deleteItemList",
        "notes": 'Remove items from shop category',
    },
}

RESERVED_PARAM_KEYS = frozenset({
    "shopId", "merchantId", "skipDepCheck", "body", "requestBody", "api", "contentType",
})

LIST_QUERY_FIELDS = frozenset()

def official_doc_url(api_name: str) -> str:
    return (
        f"https://open.shopee.com/documents/v2/v2.shop_category.{api_name}"
        f"?module={SHOPEE_DOC_MODULE}&type=1"
    )

def list_api_names() -> list[str]:
    return sorted(SHOP_CATEGORY_ENDPOINTS.keys())
