"""Shopee 店铺秒杀操作注册表（v2.shop_flash_sale.*）。"""

from __future__ import annotations

from typing import Literal, TypedDict


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
        "notes": '获取可用秒杀时段编号',
    },
    "create_shop_flash_sale": {
        "path": "api/v2/shop_flash_sale/create_shop_flash_sale",
        "method": "POST",
        "response_key": "createShopFlashSale",
        "notes": '创建店铺秒杀活动；传入完整请求体',
    },
    "get_item_criteria": {
        "path": "api/v2/shop_flash_sale/get_item_criteria",
        "method": "GET",
        "response_key": "getItemCriteria",
        "notes": '查询商品参与秒杀的条件',
    },
    "add_shop_flash_sale_items": {
        "path": "api/v2/shop_flash_sale/add_shop_flash_sale_items",
        "method": "POST",
        "response_key": "addShopFlashSaleItems",
        "notes": '添加秒杀商品',
    },
    "get_shop_flash_sale_list": {
        "path": "api/v2/shop_flash_sale/get_shop_flash_sale_list",
        "method": "GET",
        "response_key": "getShopFlashSaleList",
        "notes": '查询秒杀活动列表；分页与状态筛选',
    },
    "get_shop_flash_sale": {
        "path": "api/v2/shop_flash_sale/get_shop_flash_sale",
        "method": "GET",
        "response_key": "getShopFlashSale",
        "notes": '按 flash_sale_id 查询活动详情',
    },
    "get_shop_flash_sale_items": {
        "path": "api/v2/shop_flash_sale/get_shop_flash_sale_items",
        "method": "GET",
        "response_key": "getShopFlashSaleItems",
        "notes": '查询活动内商品',
    },
    "update_shop_flash_sale": {
        "path": "api/v2/shop_flash_sale/update_shop_flash_sale",
        "method": "POST",
        "response_key": "updateShopFlashSale",
        "notes": '更新秒杀活动设置',
    },
    "update_shop_flash_sale_items": {
        "path": "api/v2/shop_flash_sale/update_shop_flash_sale_items",
        "method": "POST",
        "response_key": "updateShopFlashSaleItems",
        "notes": '更新秒杀商品设置',
    },
    "delete_shop_flash_sale": {
        "path": "api/v2/shop_flash_sale/delete_shop_flash_sale",
        "method": "POST",
        "response_key": "deleteShopFlashSale",
        "notes": '删除秒杀活动',
    },
    "delete_shop_flash_sale_items": {
        "path": "api/v2/shop_flash_sale/delete_shop_flash_sale_items",
        "method": "POST",
        "response_key": "deleteShopFlashSaleItems",
        "notes": '移除秒杀商品',
    },
}

RESERVED_PARAM_KEYS = frozenset({
    "shopId", "merchantId", "skipDepCheck", "body", "requestBody", "api", "contentType",
})

LIST_QUERY_FIELDS = frozenset()


def list_api_names() -> list[str]:
    return sorted(SHOP_FLASH_SALE_ENDPOINTS.keys())
