"""Shopee AMS 操作注册表（v2.ams.*）。"""

from __future__ import annotations

from typing import Literal, TypedDict


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
        "notes": '查询已加入开放推广的商品',
    },
    "get_open_campaign_not_added_product": {
        "path": "api/v2/ams/get_open_campaign_not_added_product",
        "method": "GET",
        "response_key": "getOpenCampaignNotAddedProduct",
        "notes": '查询未加入开放推广的商品',
    },
    "batch_add_products_to_open_campaign": {
        "path": "api/v2/ams/batch_add_products_to_open_campaign",
        "method": "POST",
        "response_key": "batchAddProductsToOpenCampaign",
        "notes": '批量添加开放推广商品',
    },
    "add_all_products_to_open_campaign": {
        "path": "api/v2/ams/add_all_products_to_open_campaign",
        "method": "POST",
        "response_key": "addAllProductsToOpenCampaign",
        "notes": '将全部合格商品加入开放推广',
    },
    "get_auto_add_new_product_toggle_status": {
        "path": "api/v2/ams/get_auto_add_new_product_toggle_status",
        "method": "GET",
        "response_key": "getAutoAddNewProductToggleStatus",
        "notes": '查询新品自动加入开关',
    },
    "update_auto_add_new_product_setting": {
        "path": "api/v2/ams/update_auto_add_new_product_setting",
        "method": "POST",
        "response_key": "updateAutoAddNewProductSetting",
        "notes": '更新新品自动加入设置',
    },
    "batch_edit_products_open_campaign_setting": {
        "path": "api/v2/ams/batch_edit_products_open_campaign_setting",
        "method": "POST",
        "response_key": "batchEditProductsOpenCampaignSetting",
        "notes": '批量编辑开放推广商品设置',
    },
    "edit_all_products_open_campaign_setting": {
        "path": "api/v2/ams/edit_all_products_open_campaign_setting",
        "method": "POST",
        "response_key": "editAllProductsOpenCampaignSetting",
        "notes": '编辑全部开放推广商品设置',
    },
    "batch_remove_products_open_campaign_setting": {
        "path": "api/v2/ams/batch_remove_products_open_campaign_setting",
        "method": "POST",
        "response_key": "batchRemoveProductsOpenCampaignSetting",
        "notes": '批量移除开放推广商品',
    },
    "remove_all_products_open_campaign_setting": {
        "path": "api/v2/ams/remove_all_products_open_campaign_setting",
        "method": "POST",
        "response_key": "removeAllProductsOpenCampaignSetting",
        "notes": '移除全部开放推广商品',
    },
    "get_open_campaign_batch_task_result": {
        "path": "api/v2/ams/get_open_campaign_batch_task_result",
        "method": "GET",
        "response_key": "getOpenCampaignBatchTaskResult",
        "notes": '查询开放推广批量任务结果',
    },
    "get_optimization_suggestion_product": {
        "path": "api/v2/ams/get_optimization_suggestion_product",
        "method": "GET",
        "response_key": "getOptimizationSuggestionProduct",
        "notes": '查询商品优化建议',
    },
    "batch_get_products_suggested_rate": {
        "path": "api/v2/ams/batch_get_products_suggested_rate",
        "method": "POST",
        "response_key": "batchGetProductsSuggestedRate",
        "notes": '批量查询商品建议佣金率',
    },
    "get_shop_suggested_rate": {
        "path": "api/v2/ams/get_shop_suggested_rate",
        "method": "GET",
        "response_key": "getShopSuggestedRate",
        "notes": '查询店铺建议佣金率',
    },
    "get_targeted_campaign_addable_product_list": {
        "path": "api/v2/ams/get_targeted_campaign_addable_product_list",
        "method": "GET",
        "response_key": "getTargetedCampaignAddableProductList",
        "notes": '查询定向推广可添加商品',
    },
    "get_recommended_affiliate_list": {
        "path": "api/v2/ams/get_recommended_affiliate_list",
        "method": "GET",
        "response_key": "getRecommendedAffiliateList",
        "notes": '查询推荐达人',
    },
    "get_managed_affiliate_list": {
        "path": "api/v2/ams/get_managed_affiliate_list",
        "method": "GET",
        "response_key": "getManagedAffiliateList",
        "notes": '查询已管理达人',
    },
    "query_affiliate_list": {
        "path": "api/v2/ams/query_affiliate_list",
        "method": "GET",
        "response_key": "queryAffiliateList",
        "notes": '筛选查询达人列表',
    },
    "create_new_targeted_campaign": {
        "path": "api/v2/ams/create_new_targeted_campaign",
        "method": "POST",
        "response_key": "createNewTargetedCampaign",
        "notes": '创建定向推广活动',
    },
    "get_targeted_campaign_list": {
        "path": "api/v2/ams/get_targeted_campaign_list",
        "method": "GET",
        "response_key": "getTargetedCampaignList",
        "notes": '查询定向推广活动列表',
    },
    "get_targeted_campaign_settings": {
        "path": "api/v2/ams/get_targeted_campaign_settings",
        "method": "GET",
        "response_key": "getTargetedCampaignSettings",
        "notes": '查询定向推广设置',
    },
    "update_basic_info_of_targeted_campaign": {
        "path": "api/v2/ams/update_basic_info_of_targeted_campaign",
        "method": "POST",
        "response_key": "updateBasicInfoOfTargetedCampaign",
        "notes": '更新定向推广基本信息',
    },
    "edit_product_list_of_targeted_campaign": {
        "path": "api/v2/ams/edit_product_list_of_targeted_campaign",
        "method": "POST",
        "response_key": "editProductListOfTargetedCampaign",
        "notes": '编辑定向推广商品列表',
    },
    "edit_affiliate_list_of_targeted_campaign": {
        "path": "api/v2/ams/edit_affiliate_list_of_targeted_campaign",
        "method": "POST",
        "response_key": "editAffiliateListOfTargetedCampaign",
        "notes": '编辑定向推广达人列表',
    },
    "terminate_targeted_campaign": {
        "path": "api/v2/ams/terminate_targeted_campaign",
        "method": "POST",
        "response_key": "terminateTargetedCampaign",
        "notes": '终止定向推广活动',
    },
    "get_performance_data_update_time": {
        "path": "api/v2/ams/get_performance_data_update_time",
        "method": "GET",
        "response_key": "getPerformanceDataUpdateTime",
        "notes": '查询效果数据更新时间',
    },
    "get_shop_performance": {
        "path": "api/v2/ams/get_shop_performance",
        "method": "GET",
        "response_key": "getShopPerformance",
        "notes": '查询店铺效果',
    },
    "get_product_performance": {
        "path": "api/v2/ams/get_product_performance",
        "method": "GET",
        "response_key": "getProductPerformance",
        "notes": '查询商品效果',
    },
    "get_affiliate_performance": {
        "path": "api/v2/ams/get_affiliate_performance",
        "method": "GET",
        "response_key": "getAffiliatePerformance",
        "notes": '查询达人效果',
    },
    "get_content_performance": {
        "path": "api/v2/ams/get_content_performance",
        "method": "GET",
        "response_key": "getContentPerformance",
        "notes": '查询内容效果',
    },
    "get_campaign_key_metrics_performance": {
        "path": "api/v2/ams/get_campaign_key_metrics_performance",
        "method": "GET",
        "response_key": "getCampaignKeyMetricsPerformance",
        "notes": '查询活动关键指标',
    },
    "get_open_campaign_performance": {
        "path": "api/v2/ams/get_open_campaign_performance",
        "method": "GET",
        "response_key": "getOpenCampaignPerformance",
        "notes": '查询开放推广效果',
    },
    "get_targeted_campaign_performance": {
        "path": "api/v2/ams/get_targeted_campaign_performance",
        "method": "GET",
        "response_key": "getTargetedCampaignPerformance",
        "notes": '查询定向推广效果',
    },
    "get_conversion_report": {
        "path": "api/v2/ams/get_conversion_report",
        "method": "GET",
        "response_key": "getConversionReport",
        "notes": '查询转化报告',
    },
    "get_validation_list": {
        "path": "api/v2/ams/get_validation_list",
        "method": "GET",
        "response_key": "getValidationList",
        "notes": '查询结算验证列表',
    },
    "get_validation_report": {
        "path": "api/v2/ams/get_validation_report",
        "method": "GET",
        "response_key": "getValidationReport",
        "notes": '查询结算验证报告',
    },
}

RESERVED_PARAM_KEYS = frozenset({
    "shopId", "merchantId", "skipDepCheck", "body", "requestBody", "api", "contentType",
})

LIST_QUERY_FIELDS = frozenset()


def list_api_names() -> list[str]:
    return sorted(AMS_ENDPOINTS.keys())
