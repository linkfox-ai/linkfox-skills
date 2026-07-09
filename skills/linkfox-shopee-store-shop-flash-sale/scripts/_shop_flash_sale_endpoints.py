"""Shopee Shop Flash Sale module API registry (v2.shop_flash_sale.*)."""

from __future__ import annotations

from typing import Literal, TypedDict

SHOPEE_DOC_MODULE = "123"

class ShopFlashSaleEndpoint(TypedDict, total=False):
    path: str
    method: Literal["GET", "POST"]
    response_key: str
    required: list[str]
    body_fields: list[str]
    notes: str

SHOP_FLASH_SALE_ENDPOINTS: dict[str, ShopFlashSaleEndpoint] = {
    "get_time_slot_id": {
        "path": "api/v2/shop_flash_sale/get_time_slot_id",
        "method": "GET",
        "response_key": "getTimeSlotId",
        "notes": 'Get available flash sale time slot IDs',
    },
    "create_shop_flash_sale": {
        "path": "api/v2/shop_flash_sale/create_shop_flash_sale",
        "method": "POST",
        "response_key": "createShopFlashSale",
        "notes": 'Create shop flash sale event; pass full body',
    },
    "get_item_criteria": {
        "path": "api/v2/shop_flash_sale/get_item_criteria",
        "method": "GET",
        "response_key": "getItemCriteria",
        "notes": 'Get item eligibility criteria for flash sale',
    },
    "add_shop_flash_sale_items": {
        "path": "api/v2/shop_flash_sale/add_shop_flash_sale_items",
        "method": "POST",
        "response_key": "addShopFlashSaleItems",
        "notes": 'Add items to flash sale',
    },
    "get_shop_flash_sale_list": {
        "path": "api/v2/shop_flash_sale/get_shop_flash_sale_list",
        "method": "GET",
        "response_key": "getShopFlashSaleList",
        "notes": 'List shop flash sales; pagination/status filters',
    },
    "get_shop_flash_sale": {
        "path": "api/v2/shop_flash_sale/get_shop_flash_sale",
        "method": "GET",
        "response_key": "getShopFlashSale",
        "notes": 'Flash sale detail by flash_sale_id',
    },
    "get_shop_flash_sale_items": {
        "path": "api/v2/shop_flash_sale/get_shop_flash_sale_items",
        "method": "GET",
        "response_key": "getShopFlashSaleItems",
        "notes": 'Items in flash sale',
    },
    "update_shop_flash_sale": {
        "path": "api/v2/shop_flash_sale/update_shop_flash_sale",
        "method": "POST",
        "response_key": "updateShopFlashSale",
        "notes": 'Update flash sale settings',
    },
    "update_shop_flash_sale_items": {
        "path": "api/v2/shop_flash_sale/update_shop_flash_sale_items",
        "method": "POST",
        "response_key": "updateShopFlashSaleItems",
        "notes": 'Update flash sale item settings',
    },
    "delete_shop_flash_sale": {
        "path": "api/v2/shop_flash_sale/delete_shop_flash_sale",
        "method": "POST",
        "response_key": "deleteShopFlashSale",
        "notes": 'Delete flash sale',
    },
    "delete_shop_flash_sale_items": {
        "path": "api/v2/shop_flash_sale/delete_shop_flash_sale_items",
        "method": "POST",
        "response_key": "deleteShopFlashSaleItems",
        "notes": 'Remove items from flash sale',
    },
}

RESERVED_PARAM_KEYS = frozenset({
    "shopId", "merchantId", "skipDepCheck", "body", "requestBody", "api", "contentType",
})

LIST_QUERY_FIELDS = frozenset()

def official_doc_url(api_name: str) -> str:
    return (
        f"https://open.shopee.com/documents/v2/v2.shop_flash_sale.{api_name}"
        f"?module={SHOPEE_DOC_MODULE}&type=1"
    )

def list_api_names() -> list[str]:
    return sorted(SHOP_FLASH_SALE_ENDPOINTS.keys())
