"""Shopee GlobalProduct module API registry (v2.global_product.*)."""

from __future__ import annotations

from typing import Literal, TypedDict

SHOPEE_DOC_MODULE = "90"


class GlobalProductEndpoint(TypedDict, total=False):
    path: str
    method: Literal["GET", "POST"]
    response_key: str
    required: list[str]
    body_fields: list[str]
    notes: str


GLOBAL_PRODUCT_ENDPOINTS: dict[str, GlobalProductEndpoint] = {
    "get_category": {
        "path": "api/v2/global_product/get_category",
        "method": "GET",
        "response_key": "getCategory",
        "notes": 'Optional language; global category tree',
    },
    "get_attribute_tree": {
        "path": "api/v2/global_product/get_attribute_tree",
        "method": "GET",
        "response_key": "getAttributeTree",
        "required": ['category_id'],
        "notes": 'Mandatory attributes for global listing',
    },
    "get_brand_list": {
        "path": "api/v2/global_product/get_brand_list",
        "method": "GET",
        "response_key": "getBrandList",
        "required": ['offset', 'page_size', 'category_id'],
        "notes": 'page_size max 100',
    },
    "get_global_item_limit": {
        "path": "api/v2/global_product/get_global_item_limit",
        "method": "GET",
        "response_key": "getGlobalItemLimit",
        "notes": 'Global item listing limits',
    },
    "get_global_item_list": {
        "path": "api/v2/global_product/get_global_item_list",
        "method": "GET",
        "response_key": "getGlobalItemList",
        "required": ['offset', 'page_size'],
        "notes": 'Optional update_time_from/to filters',
    },
    "get_global_item_info": {
        "path": "api/v2/global_product/get_global_item_info",
        "method": "GET",
        "response_key": "getGlobalItemInfo",
        "required": ['global_item_id_list'],
        "notes": 'max 50, comma-separated',
    },
    "add_global_item": {
        "path": "api/v2/global_product/add_global_item",
        "method": "POST",
        "response_key": "addGlobalItem",
        "notes": 'Complex body — pass body with category_id, global_item_name, etc.',
    },
    "update_global_item": {
        "path": "api/v2/global_product/update_global_item",
        "method": "POST",
        "response_key": "updateGlobalItem",
        "notes": 'Pass body with global_item_id and fields to update',
    },
    "delete_global_item": {
        "path": "api/v2/global_product/delete_global_item",
        "method": "POST",
        "response_key": "deleteGlobalItem",
        "required": ['global_item_id'],
        "body_fields": ['global_item_id'],
        "notes": 'Delete global item',
    },
    "init_tier_variation": {
        "path": "api/v2/global_product/init_tier_variation",
        "method": "POST",
        "response_key": "initTierVariation",
        "notes": 'Initialize global SKU tier variation',
    },
    "update_tier_variation": {
        "path": "api/v2/global_product/update_tier_variation",
        "method": "POST",
        "response_key": "updateTierVariation",
        "notes": 'Update tier variation structure',
    },
    "add_global_model": {
        "path": "api/v2/global_product/add_global_model",
        "method": "POST",
        "response_key": "addGlobalModel",
        "notes": 'Add global SKU model',
    },
    "update_global_model": {
        "path": "api/v2/global_product/update_global_model",
        "method": "POST",
        "response_key": "updateGlobalModel",
        "notes": 'Update global SKU model',
    },
    "delete_global_model": {
        "path": "api/v2/global_product/delete_global_model",
        "method": "POST",
        "response_key": "deleteGlobalModel",
        "notes": 'Delete global SKU model',
    },
    "get_global_model_list": {
        "path": "api/v2/global_product/get_global_model_list",
        "method": "GET",
        "response_key": "getGlobalModelList",
        "required": ['global_item_id'],
        "notes": 'Global SKU/model list',
    },
    "support_size_chart": {
        "path": "api/v2/global_product/support_size_chart",
        "method": "POST",
        "response_key": "supportSizeChart",
        "notes": 'Check size chart support for category',
    },
    "update_size_chart": {
        "path": "api/v2/global_product/update_size_chart",
        "method": "POST",
        "response_key": "updateSizeChart",
        "notes": 'Update size chart on global item',
    },
    "create_publish_task": {
        "path": "api/v2/global_product/create_publish_task",
        "method": "POST",
        "response_key": "createPublishTask",
        "notes": 'Publish global item to shop(s); pass full body',
    },
    "get_publishable_shop": {
        "path": "api/v2/global_product/get_publishable_shop",
        "method": "GET",
        "response_key": "getPublishableShop",
        "notes": 'Shops eligible for publish',
    },
    "get_publish_task_result": {
        "path": "api/v2/global_product/get_publish_task_result",
        "method": "GET",
        "response_key": "getPublishTaskResult",
        "notes": 'Publish task status by task_id',
    },
    "get_published_list": {
        "path": "api/v2/global_product/get_published_list",
        "method": "GET",
        "response_key": "getPublishedList",
        "notes": 'Published global items per shop',
    },
    "update_price": {
        "path": "api/v2/global_product/update_price",
        "method": "POST",
        "response_key": "updatePrice",
        "notes": 'Body: global_item_id + price_list',
    },
    "update_stock": {
        "path": "api/v2/global_product/update_stock",
        "method": "POST",
        "response_key": "updateStock",
        "notes": 'Body: global_item_id + stock_list',
    },
    "set_sync_field": {
        "path": "api/v2/global_product/set_sync_field",
        "method": "POST",
        "response_key": "setSyncField",
        "notes": 'Set sync fields for published items',
    },
    "get_global_item_id": {
        "path": "api/v2/global_product/get_global_item_id",
        "method": "GET",
        "response_key": "getGlobalItemId",
        "notes": 'Map shop item_id to global_item_id',
    },
    "category_recommend": {
        "path": "api/v2/global_product/category_recommend",
        "method": "POST",
        "response_key": "categoryRecommend",
        "notes": 'Recommend category from item name/image',
    },
    "get_recommend_attribute": {
        "path": "api/v2/global_product/get_recommend_attribute",
        "method": "POST",
        "response_key": "getRecommendAttribute",
        "notes": 'Recommend attributes for global listing',
    },
    "get_shop_publishable_status": {
        "path": "api/v2/global_product/get_shop_publishable_status",
        "method": "GET",
        "response_key": "getShopPublishableStatus",
        "notes": 'Shop publish eligibility status',
    },
    "get_variations": {
        "path": "api/v2/global_product/get_variations",
        "method": "GET",
        "response_key": "getVariations",
        "notes": 'Standard variation options',
    },
    "get_size_chart_detail": {
        "path": "api/v2/global_product/get_size_chart_detail",
        "method": "GET",
        "response_key": "getSizeChartDetail",
        "notes": 'Size chart detail by size_chart_id',
    },
    "get_size_chart_list": {
        "path": "api/v2/global_product/get_size_chart_list",
        "method": "GET",
        "response_key": "getSizeChartList",
        "notes": 'Size charts for category',
    },
    "search_global_attribute_value_list": {
        "path": "api/v2/global_product/search_global_attribute_value_list",
        "method": "POST",
        "response_key": "searchGlobalAttributeValueList",
        "notes": 'Search global attribute values',
    },
    "get_local_adjustment_rate": {
        "path": "api/v2/global_product/get_local_adjustment_rate",
        "method": "GET",
        "response_key": "getLocalAdjustmentRate",
        "notes": 'Local price adjustment rate',
    },
    "update_local_adjustment_rate": {
        "path": "api/v2/global_product/update_local_adjustment_rate",
        "method": "POST",
        "response_key": "updateLocalAdjustmentRate",
        "notes": 'Update local price adjustment rate',
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

LIST_QUERY_FIELDS = frozenset({
    "global_item_id_list",
    "item_id_list",
})


def official_doc_url(api_name: str) -> str:
    return (
        f"https://open.shopee.com/documents/v2/v2.global_product.{api_name}"
        f"?module={SHOPEE_DOC_MODULE}&type=1"
    )


def list_api_names() -> list[str]:
    return sorted(GLOBAL_PRODUCT_ENDPOINTS.keys())
