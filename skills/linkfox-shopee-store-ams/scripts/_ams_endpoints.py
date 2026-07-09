"""Shopee AMS module API registry (v2.ams.*)."""

from __future__ import annotations

from typing import Literal, TypedDict

SHOPEE_DOC_MODULE = "127"

class AmsEndpoint(TypedDict, total=False):
    path: str
    method: Literal["GET", "POST"]
    response_key: str
    required: list[str]
    body_fields: list[str]
    notes: str

AMS_ENDPOINTS: dict[str, AmsEndpoint] = {
    "get_open_campaign_added_product": {
        "path": "api/v2/ams/get_open_campaign_added_product",
        "method": "GET",
        "response_key": "getOpenCampaignAddedProduct",
        "notes": 'Products in Open Campaign',
    },
    "get_open_campaign_not_added_product": {
        "path": "api/v2/ams/get_open_campaign_not_added_product",
        "method": "GET",
        "response_key": "getOpenCampaignNotAddedProduct",
        "notes": 'Products not yet in Open Campaign',
    },
    "batch_add_products_to_open_campaign": {
        "path": "api/v2/ams/batch_add_products_to_open_campaign",
        "method": "POST",
        "response_key": "batchAddProductsToOpenCampaign",
        "notes": 'Batch add products to Open Campaign',
    },
    "add_all_products_to_open_campaign": {
        "path": "api/v2/ams/add_all_products_to_open_campaign",
        "method": "POST",
        "response_key": "addAllProductsToOpenCampaign",
        "notes": 'Add all eligible products to Open Campaign',
    },
    "get_auto_add_new_product_toggle_status": {
        "path": "api/v2/ams/get_auto_add_new_product_toggle_status",
        "method": "GET",
        "response_key": "getAutoAddNewProductToggleStatus",
        "notes": 'Auto-add new product toggle status',
    },
    "update_auto_add_new_product_setting": {
        "path": "api/v2/ams/update_auto_add_new_product_setting",
        "method": "POST",
        "response_key": "updateAutoAddNewProductSetting",
        "notes": 'Update auto-add new product setting',
    },
    "batch_edit_products_open_campaign_setting": {
        "path": "api/v2/ams/batch_edit_products_open_campaign_setting",
        "method": "POST",
        "response_key": "batchEditProductsOpenCampaignSetting",
        "notes": 'Batch edit Open Campaign product settings',
    },
    "edit_all_products_open_campaign_setting": {
        "path": "api/v2/ams/edit_all_products_open_campaign_setting",
        "method": "POST",
        "response_key": "editAllProductsOpenCampaignSetting",
        "notes": 'Edit all products Open Campaign settings',
    },
    "batch_remove_products_open_campaign_setting": {
        "path": "api/v2/ams/batch_remove_products_open_campaign_setting",
        "method": "POST",
        "response_key": "batchRemoveProductsOpenCampaignSetting",
        "notes": 'Batch remove products from Open Campaign',
    },
    "remove_all_products_open_campaign_setting": {
        "path": "api/v2/ams/remove_all_products_open_campaign_setting",
        "method": "POST",
        "response_key": "removeAllProductsOpenCampaignSetting",
        "notes": 'Remove all products from Open Campaign',
    },
    "get_open_campaign_batch_task_result": {
        "path": "api/v2/ams/get_open_campaign_batch_task_result",
        "method": "GET",
        "response_key": "getOpenCampaignBatchTaskResult",
        "notes": 'Batch task result for Open Campaign ops',
    },
    "get_optimization_suggestion_product": {
        "path": "api/v2/ams/get_optimization_suggestion_product",
        "method": "GET",
        "response_key": "getOptimizationSuggestionProduct",
        "notes": 'Product optimization suggestions',
    },
    "batch_get_products_suggested_rate": {
        "path": "api/v2/ams/batch_get_products_suggested_rate",
        "method": "POST",
        "response_key": "batchGetProductsSuggestedRate",
        "notes": 'Batch get suggested commission rates',
    },
    "get_shop_suggested_rate": {
        "path": "api/v2/ams/get_shop_suggested_rate",
        "method": "GET",
        "response_key": "getShopSuggestedRate",
        "notes": 'Shop suggested commission rate',
    },
    "get_targeted_campaign_addable_product_list": {
        "path": "api/v2/ams/get_targeted_campaign_addable_product_list",
        "method": "GET",
        "response_key": "getTargetedCampaignAddableProductList",
        "notes": 'Products addable to targeted campaign',
    },
    "get_recommended_affiliate_list": {
        "path": "api/v2/ams/get_recommended_affiliate_list",
        "method": "GET",
        "response_key": "getRecommendedAffiliateList",
        "notes": 'Recommended affiliates',
    },
    "get_managed_affiliate_list": {
        "path": "api/v2/ams/get_managed_affiliate_list",
        "method": "GET",
        "response_key": "getManagedAffiliateList",
        "notes": 'Managed affiliates',
    },
    "query_affiliate_list": {
        "path": "api/v2/ams/query_affiliate_list",
        "method": "GET",
        "response_key": "queryAffiliateList",
        "notes": 'Query affiliate list with filters',
    },
    "create_new_targeted_campaign": {
        "path": "api/v2/ams/create_new_targeted_campaign",
        "method": "POST",
        "response_key": "createNewTargetedCampaign",
        "notes": 'Create targeted affiliate campaign',
    },
    "get_targeted_campaign_list": {
        "path": "api/v2/ams/get_targeted_campaign_list",
        "method": "GET",
        "response_key": "getTargetedCampaignList",
        "notes": 'Targeted campaign list',
    },
    "get_targeted_campaign_settings": {
        "path": "api/v2/ams/get_targeted_campaign_settings",
        "method": "GET",
        "response_key": "getTargetedCampaignSettings",
        "notes": 'Targeted campaign settings detail',
    },
    "update_basic_info_of_targeted_campaign": {
        "path": "api/v2/ams/update_basic_info_of_targeted_campaign",
        "method": "POST",
        "response_key": "updateBasicInfoOfTargetedCampaign",
        "notes": 'Update targeted campaign basic info',
    },
    "edit_product_list_of_targeted_campaign": {
        "path": "api/v2/ams/edit_product_list_of_targeted_campaign",
        "method": "POST",
        "response_key": "editProductListOfTargetedCampaign",
        "notes": 'Edit products in targeted campaign',
    },
    "edit_affiliate_list_of_targeted_campaign": {
        "path": "api/v2/ams/edit_affiliate_list_of_targeted_campaign",
        "method": "POST",
        "response_key": "editAffiliateListOfTargetedCampaign",
        "notes": 'Edit affiliates in targeted campaign',
    },
    "terminate_targeted_campaign": {
        "path": "api/v2/ams/terminate_targeted_campaign",
        "method": "POST",
        "response_key": "terminateTargetedCampaign",
        "notes": 'Terminate targeted campaign',
    },
    "get_performance_data_update_time": {
        "path": "api/v2/ams/get_performance_data_update_time",
        "method": "GET",
        "response_key": "getPerformanceDataUpdateTime",
        "notes": 'Performance data last update time',
    },
    "get_shop_performance": {
        "path": "api/v2/ams/get_shop_performance",
        "method": "GET",
        "response_key": "getShopPerformance",
        "notes": 'Shop AMS performance',
    },
    "get_product_performance": {
        "path": "api/v2/ams/get_product_performance",
        "method": "GET",
        "response_key": "getProductPerformance",
        "notes": 'Product AMS performance',
    },
    "get_affiliate_performance": {
        "path": "api/v2/ams/get_affiliate_performance",
        "method": "GET",
        "response_key": "getAffiliatePerformance",
        "notes": 'Affiliate performance',
    },
    "get_content_performance": {
        "path": "api/v2/ams/get_content_performance",
        "method": "GET",
        "response_key": "getContentPerformance",
        "notes": 'Content performance',
    },
    "get_campaign_key_metrics_performance": {
        "path": "api/v2/ams/get_campaign_key_metrics_performance",
        "method": "GET",
        "response_key": "getCampaignKeyMetricsPerformance",
        "notes": 'Campaign key metrics',
    },
    "get_open_campaign_performance": {
        "path": "api/v2/ams/get_open_campaign_performance",
        "method": "GET",
        "response_key": "getOpenCampaignPerformance",
        "notes": 'Open Campaign performance',
    },
    "get_targeted_campaign_performance": {
        "path": "api/v2/ams/get_targeted_campaign_performance",
        "method": "GET",
        "response_key": "getTargetedCampaignPerformance",
        "notes": 'Targeted campaign performance',
    },
    "get_conversion_report": {
        "path": "api/v2/ams/get_conversion_report",
        "method": "GET",
        "response_key": "getConversionReport",
        "notes": 'Conversion report',
    },
    "get_validation_list": {
        "path": "api/v2/ams/get_validation_list",
        "method": "GET",
        "response_key": "getValidationList",
        "notes": 'Validation list',
    },
    "get_validation_report": {
        "path": "api/v2/ams/get_validation_report",
        "method": "GET",
        "response_key": "getValidationReport",
        "notes": 'Validation report',
    },
}

RESERVED_PARAM_KEYS = frozenset({
    "shopId", "merchantId", "skipDepCheck", "body", "requestBody", "api", "contentType",
})

LIST_QUERY_FIELDS = frozenset()

def official_doc_url(api_name: str) -> str:
    return (
        f"https://open.shopee.com/documents/v2/v2.ams.{api_name}"
        f"?module={SHOPEE_DOC_MODULE}&type=1"
    )

def list_api_names() -> list[str]:
    return sorted(AMS_ENDPOINTS.keys())
