"""Shopee Product module API registry (v2.product.*)."""

from __future__ import annotations

from typing import Literal, TypedDict

SHOPEE_DOC_MODULE = "89"


class ProductEndpoint(TypedDict, total=False):
    path: str
    method: Literal["GET", "POST"]
    response_key: str
    required: list[str]
    body_fields: list[str]
    notes: str


PRODUCT_ENDPOINTS: dict[str, ProductEndpoint] = {
    "get_category": {
        "path": "api/v2/product/get_category",
        "method": "GET",
        "response_key": "getCategory",
        "notes": 'Optional language; returns category_list tree',
    },
    "get_attribute_tree": {
        "path": "api/v2/product/get_attribute_tree",
        "method": "GET",
        "response_key": "getAttributeTree",
        "required": ['category_id'],
        "notes": 'Mandatory attributes for listing in category',
    },
    "get_brand_list": {
        "path": "api/v2/product/get_brand_list",
        "method": "GET",
        "response_key": "getBrandList",
        "required": ['offset', 'page_size', 'category_id'],
        "notes": 'page_size max 100',
    },
    "get_item_limit": {
        "path": "api/v2/product/get_item_limit",
        "method": "GET",
        "response_key": "getItemLimit",
        "notes": 'Shop listing limits',
    },
    "get_item_list": {
        "path": "api/v2/product/get_item_list",
        "method": "GET",
        "response_key": "getItemList",
        "required": ['offset', 'page_size'],
        "notes": 'item_status optional: NORMAL/BANNED/DELETED/UNLIST',
    },
    "get_item_base_info": {
        "path": "api/v2/product/get_item_base_info",
        "method": "GET",
        "response_key": "getItemBaseInfo",
        "required": ['item_id_list'],
        "notes": 'item_id_list max 50, comma-separated',
    },
    "get_item_extra_info": {
        "path": "api/v2/product/get_item_extra_info",
        "method": "GET",
        "response_key": "getItemExtraInfo",
        "required": ['item_id_list'],
        "notes": 'Sales/views/likes etc.; max 50 items',
    },
    "add_item": {
        "path": "api/v2/product/add_item",
        "method": "POST",
        "response_key": "addItem",
        "notes": 'Complex body — pass body with category_id, item_name, price, etc.',
    },
    "update_item": {
        "path": "api/v2/product/update_item",
        "method": "POST",
        "response_key": "updateItem",
        "notes": 'Pass body with item_id and fields to update',
    },
    "delete_item": {
        "path": "api/v2/product/delete_item",
        "method": "POST",
        "response_key": "deleteItem",
        "required": ['item_id'],
        "body_fields": ['item_id'],
        "notes": 'Permanently delete item',
    },
    "init_tier_variation": {
        "path": "api/v2/product/init_tier_variation",
        "method": "POST",
        "response_key": "initTierVariation",
        "notes": 'Initialize SKU tier variation; pass full body',
    },
    "update_tier_variation": {
        "path": "api/v2/product/update_tier_variation",
        "method": "POST",
        "response_key": "updateTierVariation",
        "notes": 'Update tier variation structure',
    },
    "get_model_list": {
        "path": "api/v2/product/get_model_list",
        "method": "GET",
        "response_key": "getModelList",
        "required": ['item_id'],
        "notes": 'SKU/model list for item',
    },
    "add_model": {
        "path": "api/v2/product/add_model",
        "method": "POST",
        "response_key": "addModel",
        "notes": 'Add SKU model to item',
    },
    "update_model": {
        "path": "api/v2/product/update_model",
        "method": "POST",
        "response_key": "updateModel",
        "notes": 'Update SKU model',
    },
    "delete_model": {
        "path": "api/v2/product/delete_model",
        "method": "POST",
        "response_key": "deleteModel",
        "notes": 'Delete SKU model',
    },
    "unlist_item": {
        "path": "api/v2/product/unlist_item",
        "method": "POST",
        "response_key": "unlistItem",
        "notes": 'Body: item_list with item_id and unlist flags',
    },
    "update_price": {
        "path": "api/v2/product/update_price",
        "method": "POST",
        "response_key": "updatePrice",
        "notes": 'Body: item_id + price_list',
    },
    "update_stock": {
        "path": "api/v2/product/update_stock",
        "method": "POST",
        "response_key": "updateStock",
        "notes": 'Body: item_id + stock_list',
    },
    "boost_item": {
        "path": "api/v2/product/boost_item",
        "method": "POST",
        "response_key": "boostItem",
        "notes": 'Body: item_id_list (max 5)',
    },
    "get_boosted_list": {
        "path": "api/v2/product/get_boosted_list",
        "method": "GET",
        "response_key": "getBoostedList",
        "notes": 'Currently boosted items',
    },
    "get_item_promotion": {
        "path": "api/v2/product/get_item_promotion",
        "method": "GET",
        "response_key": "getItemPromotion",
        "required": ['item_id_list'],
        "notes": 'Promotion info; max 50 items',
    },
    "update_sip_item_price": {
        "path": "api/v2/product/update_sip_item_price",
        "method": "POST",
        "response_key": "updateSipItemPrice",
        "notes": 'SIP cross-border price update',
    },
    "search_item": {
        "path": "api/v2/product/search_item",
        "method": "GET",
        "response_key": "searchItem",
        "notes": 'Search shop items; item_name keyword etc.',
    },
    "get_comment": {
        "path": "api/v2/product/get_comment",
        "method": "GET",
        "response_key": "getComment",
        "notes": 'Product comments/reviews',
    },
    "reply_comment": {
        "path": "api/v2/product/reply_comment",
        "method": "POST",
        "response_key": "replyComment",
        "notes": 'Reply to buyer comment',
    },
    "category_recommend": {
        "path": "api/v2/product/category_recommend",
        "method": "POST",
        "response_key": "categoryRecommend",
        "notes": 'Recommend category from item name/image',
    },
    "register_brand": {
        "path": "api/v2/product/register_brand",
        "method": "POST",
        "response_key": "registerBrand",
        "notes": 'Register new brand',
    },
    "get_recommend_attribute": {
        "path": "api/v2/product/get_recommend_attribute",
        "method": "POST",
        "response_key": "getRecommendAttribute",
        "notes": 'Recommend attributes for listing',
    },
    "get_weight_recommendation": {
        "path": "api/v2/product/get_weight_recommendation",
        "method": "POST",
        "response_key": "getWeightRecommendation",
        "notes": 'Weight recommendation for category',
    },
    "get_size_chart_list": {
        "path": "api/v2/product/get_size_chart_list",
        "method": "GET",
        "response_key": "getSizeChartList",
        "notes": 'Size charts for category',
    },
    "get_size_chart_detail": {
        "path": "api/v2/product/get_size_chart_detail",
        "method": "GET",
        "response_key": "getSizeChartDetail",
        "notes": 'Size chart detail by size_chart_id',
    },
    "get_item_violation_info": {
        "path": "api/v2/product/get_item_violation_info",
        "method": "GET",
        "response_key": "getItemViolationInfo",
        "notes": 'Listing violation info',
    },
    "get_variations": {
        "path": "api/v2/product/get_variations",
        "method": "GET",
        "response_key": "getVariations",
        "notes": 'Standard variation options',
    },
    "get_all_vehicle_list": {
        "path": "api/v2/product/get_all_vehicle_list",
        "method": "GET",
        "response_key": "getAllVehicleList",
        "notes": 'Vehicle compatibility lists',
    },
    "get_vehicle_list_by_compatibility_detail": {
        "path": "api/v2/product/get_vehicle_list_by_compatibility_detail",
        "method": "GET",
        "response_key": "getVehicleListByCompatibilityDetail",
        "notes": 'Vehicles by compatibility detail',
    },
    "get_item_content_diagnosis_result": {
        "path": "api/v2/product/get_item_content_diagnosis_result",
        "method": "GET",
        "response_key": "getItemContentDiagnosisResult",
        "notes": 'Content quality diagnosis',
    },
    "get_item_list_by_content_diagnosis": {
        "path": "api/v2/product/get_item_list_by_content_diagnosis",
        "method": "GET",
        "response_key": "getItemListByContentDiagnosis",
        "notes": 'Items by diagnosis status',
    },
    "get_kit_item_limit": {
        "path": "api/v2/product/get_kit_item_limit",
        "method": "GET",
        "response_key": "getKitItemLimit",
        "notes": 'Kit/combo item limits',
    },
    "add_kit_item": {
        "path": "api/v2/product/add_kit_item",
        "method": "POST",
        "response_key": "addKitItem",
        "notes": 'Create kit/combo item',
    },
    "update_kit_item": {
        "path": "api/v2/product/update_kit_item",
        "method": "POST",
        "response_key": "updateKitItem",
        "notes": 'Update kit item',
    },
    "get_kit_item_info": {
        "path": "api/v2/product/get_kit_item_info",
        "method": "GET",
        "response_key": "getKitItemInfo",
        "notes": 'Kit item detail',
    },
    "get_ssp_list": {
        "path": "api/v2/product/get_ssp_list",
        "method": "GET",
        "response_key": "getSspList",
        "notes": 'Shopee Standard Product list',
    },
    "get_ssp_info": {
        "path": "api/v2/product/get_ssp_info",
        "method": "GET",
        "response_key": "getSspInfo",
        "notes": 'SSP detail',
    },
    "link_ssp": {
        "path": "api/v2/product/link_ssp",
        "method": "POST",
        "response_key": "linkSsp",
        "notes": 'Link item to SSP',
    },
    "unlink_ssp": {
        "path": "api/v2/product/unlink_ssp",
        "method": "POST",
        "response_key": "unlinkSsp",
        "notes": 'Unlink item from SSP',
    },
    "get_aitem_by_pitem_id": {
        "path": "api/v2/product/get_aitem_by_pitem_id",
        "method": "GET",
        "response_key": "getAitemByPitemId",
        "notes": 'Affiliate item by parent item id',
    },
    "search_attribute_value_list": {
        "path": "api/v2/product/search_attribute_value_list",
        "method": "POST",
        "response_key": "searchAttributeValueList",
        "notes": 'Search attribute values',
    },
    "get_main_item_list": {
        "path": "api/v2/product/get_main_item_list",
        "method": "GET",
        "response_key": "getMainItemList",
        "notes": 'Main shop items (direct shop)',
    },
    "get_direct_item_list": {
        "path": "api/v2/product/get_direct_item_list",
        "method": "GET",
        "response_key": "getDirectItemList",
        "notes": 'Direct shop item list',
    },
    "get_direct_shop_recommended_price": {
        "path": "api/v2/product/get_direct_shop_recommended_price",
        "method": "POST",
        "response_key": "getDirectShopRecommendedPrice",
        "notes": 'Recommended price for direct shop',
    },
    "get_product_certification_rule": {
        "path": "api/v2/product/get_product_certification_rule",
        "method": "GET",
        "response_key": "getProductCertificationRule",
        "notes": 'Product certification rules',
    },
    "publish_item_to_outlet_shop": {
        "path": "api/v2/product/publish_item_to_outlet_shop",
        "method": "POST",
        "response_key": "publishItemToOutletShop",
        "notes": 'Publish item to outlet shop',
    },
    "get_mart_item_mapping_by_id": {
        "path": "api/v2/product/get_mart_item_mapping_by_id",
        "method": "GET",
        "response_key": "getMartItemMappingById",
        "notes": 'Mart/outlet item mapping',
    },
    "search_unpackaged_model_list": {
        "path": "api/v2/product/search_unpackaged_model_list",
        "method": "POST",
        "response_key": "searchUnpackagedModelList",
        "notes": 'Search unpackaged models',
    },
    "generate_kit_image": {
        "path": "api/v2/product/generate_kit_image",
        "method": "POST",
        "response_key": "generateKitImage",
        "notes": 'Generate kit product image',
    },
    "get_mart_item_by_outlet_item_id": {
        "path": "api/v2/product/get_mart_item_by_outlet_item_id",
        "method": "GET",
        "response_key": "getMartItemByOutletItemId",
        "notes": 'Mart item by outlet item id',
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
    "item_id_list",
})


def official_doc_url(api_name: str) -> str:
    return (
        f"https://open.shopee.com/documents/v2/v2.product.{api_name}"
        f"?module={SHOPEE_DOC_MODULE}&type=1"
    )


def list_api_names() -> list[str]:
    return sorted(PRODUCT_ENDPOINTS.keys())
