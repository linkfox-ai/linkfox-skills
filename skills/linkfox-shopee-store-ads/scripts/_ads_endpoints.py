"""Shopee Ads module API registry (v2.ads.*)."""

from __future__ import annotations

from typing import Literal, TypedDict

SHOPEE_DOC_MODULE = "117"

class AdsEndpoint(TypedDict, total=False):
    path: str
    method: Literal["GET", "POST"]
    response_key: str
    required: list[str]
    body_fields: list[str]
    notes: str

ADS_ENDPOINTS: dict[str, AdsEndpoint] = {
    "get_total_balance": {
        "path": "api/v2/ads/get_total_balance",
        "method": "GET",
        "response_key": "getTotalBalance",
        "notes": 'Real-time ads credit balance',
    },
    "get_shop_toggle_info": {
        "path": "api/v2/ads/get_shop_toggle_info",
        "method": "GET",
        "response_key": "getShopToggleInfo",
        "notes": 'Auto top-up, campaign surge toggle status',
    },
    "get_recommended_keyword_list": {
        "path": "api/v2/ads/get_recommended_keyword_list",
        "method": "GET",
        "response_key": "getRecommendedKeywordList",
        "notes": 'Recommended keywords for ads',
    },
    "get_recommended_item_list": {
        "path": "api/v2/ads/get_recommended_item_list",
        "method": "GET",
        "response_key": "getRecommendedItemList",
        "notes": 'Recommended items for ads',
    },
    "get_all_cpc_ads_hourly_performance": {
        "path": "api/v2/ads/get_all_cpc_ads_hourly_performance",
        "method": "GET",
        "response_key": "getAllCpcAdsHourlyPerformance",
        "notes": 'All CPC ads hourly performance',
    },
    "get_all_cpc_ads_daily_performance": {
        "path": "api/v2/ads/get_all_cpc_ads_daily_performance",
        "method": "GET",
        "response_key": "getAllCpcAdsDailyPerformance",
        "notes": 'All CPC ads daily performance',
    },
    "get_product_campaign_daily_performance": {
        "path": "api/v2/ads/get_product_campaign_daily_performance",
        "method": "GET",
        "response_key": "getProductCampaignDailyPerformance",
        "notes": 'Product campaign daily performance',
    },
    "get_product_campaign_hourly_performance": {
        "path": "api/v2/ads/get_product_campaign_hourly_performance",
        "method": "GET",
        "response_key": "getProductCampaignHourlyPerformance",
        "notes": 'Product campaign hourly performance',
    },
    "get_product_level_campaign_id_list": {
        "path": "api/v2/ads/get_product_level_campaign_id_list",
        "method": "GET",
        "response_key": "getProductLevelCampaignIdList",
        "notes": 'Product-level campaign IDs',
    },
    "get_product_level_campaign_setting_info": {
        "path": "api/v2/ads/get_product_level_campaign_setting_info",
        "method": "GET",
        "response_key": "getProductLevelCampaignSettingInfo",
        "notes": 'Product campaign settings',
    },
    "create_manual_product_ads": {
        "path": "api/v2/ads/create_manual_product_ads",
        "method": "POST",
        "response_key": "createManualProductAds",
        "notes": 'Create manual selection product ads; pass full body',
    },
    "edit_manual_product_ad_keywords": {
        "path": "api/v2/ads/edit_manual_product_ad_keywords",
        "method": "POST",
        "response_key": "editManualProductAdKeywords",
        "notes": 'Edit manual product ad keywords',
    },
    "edit_manual_product_ads": {
        "path": "api/v2/ads/edit_manual_product_ads",
        "method": "POST",
        "response_key": "editManualProductAds",
        "notes": 'Edit manual product ads',
    },
    "get_create_product_ad_budget_suggestion": {
        "path": "api/v2/ads/get_create_product_ad_budget_suggestion",
        "method": "GET",
        "response_key": "getCreateProductAdBudgetSuggestion",
        "notes": 'Budget suggestion for new product ad',
    },
    "get_product_recommended_roi_target": {
        "path": "api/v2/ads/get_product_recommended_roi_target",
        "method": "GET",
        "response_key": "getProductRecommendedRoiTarget",
        "notes": 'Recommended ROI target',
    },
    "get_ads_facil_shop_rate": {
        "path": "api/v2/ads/get_ads_facil_shop_rate",
        "method": "GET",
        "response_key": "getAdsFacilShopRate",
        "notes": 'Ads Facil program shop rate (official: facil)',
    },
    "check_create_gms_product_campaign_eligibility": {
        "path": "api/v2/ads/check_create_gms_product_campaign_eligibility",
        "method": "GET",
        "response_key": "checkCreateGmsProductCampaignEligibility",
        "notes": 'GMS product campaign eligibility',
    },
    "create_gms_product_campaign": {
        "path": "api/v2/ads/create_gms_product_campaign",
        "method": "POST",
        "response_key": "createGmsProductCampaign",
        "notes": 'Create GMS product campaign',
    },
    "edit_gms_product_campaign": {
        "path": "api/v2/ads/edit_gms_product_campaign",
        "method": "POST",
        "response_key": "editGmsProductCampaign",
        "notes": 'Edit GMS product campaign',
    },
    "list_gms_user_deleted_item": {
        "path": "api/v2/ads/list_gms_user_deleted_item",
        "method": "GET",
        "response_key": "listGmsUserDeletedItem",
        "notes": 'GMS user-deleted items list',
    },
    "edit_gms_item_product_campaign": {
        "path": "api/v2/ads/edit_gms_item_product_campaign",
        "method": "POST",
        "response_key": "editGmsItemProductCampaign",
        "notes": 'Edit GMS item product campaign',
    },
    "get_gms_campaign_performance": {
        "path": "api/v2/ads/get_gms_campaign_performance",
        "method": "GET",
        "response_key": "getGmsCampaignPerformance",
        "notes": 'GMS campaign performance',
    },
    "get_gms_item_performance": {
        "path": "api/v2/ads/get_gms_item_performance",
        "method": "GET",
        "response_key": "getGmsItemPerformance",
        "notes": 'GMS item performance',
    },
}

RESERVED_PARAM_KEYS = frozenset({
    "shopId", "merchantId", "skipDepCheck", "body", "requestBody", "api", "contentType",
})

LIST_QUERY_FIELDS = frozenset()

def official_doc_url(api_name: str) -> str:
    return (
        f"https://open.shopee.com/documents/v2/v2.ads.{api_name}"
        f"?module={SHOPEE_DOC_MODULE}&type=1"
    )

def list_api_names() -> list[str]:
    return sorted(ADS_ENDPOINTS.keys())
