"""Shopee Account Health module API registry (v2.account_health.*)."""

from __future__ import annotations

from typing import Literal, TypedDict

SHOPEE_DOC_MODULE = "103"

class AccountHealthEndpoint(TypedDict, total=False):
    path: str
    method: Literal["GET", "POST"]
    response_key: str
    required: list[str]
    body_fields: list[str]
    notes: str

ACCOUNT_HEALTH_ENDPOINTS: dict[str, AccountHealthEndpoint] = {
    "get_shop_performance": {
        "path": "api/v2/account_health/get_shop_performance",
        "method": "GET",
        "response_key": "getShopPerformance",
        "notes": 'Shop performance metrics and overall health',
    },
    "get_metric_source_detail": {
        "path": "api/v2/account_health/get_metric_source_detail",
        "method": "GET",
        "response_key": "getMetricSourceDetail",
        "notes": 'Metric source detail by metric_id',
    },
    "get_penalty_point_history": {
        "path": "api/v2/account_health/get_penalty_point_history",
        "method": "GET",
        "response_key": "getPenaltyPointHistory",
        "notes": 'Penalty point history; pagination filters',
    },
    "get_punishment_history": {
        "path": "api/v2/account_health/get_punishment_history",
        "method": "GET",
        "response_key": "getPunishmentHistory",
        "notes": 'Punishment history; pagination filters',
    },
    "get_listings_with_issues": {
        "path": "api/v2/account_health/get_listings_with_issues",
        "method": "GET",
        "response_key": "getListingsWithIssues",
        "notes": 'Listings with health issues',
    },
    "get_late_orders": {
        "path": "api/v2/account_health/get_late_orders",
        "method": "GET",
        "response_key": "getLateOrders",
        "notes": 'Late orders requiring action; page_no/page_size',
    },
}

RESERVED_PARAM_KEYS = frozenset({
    "shopId", "merchantId", "skipDepCheck", "body", "requestBody", "api", "contentType",
})

LIST_QUERY_FIELDS = frozenset()

def official_doc_url(api_name: str) -> str:
    return (
        f"https://open.shopee.com/documents/v2/v2.account_health.{api_name}"
        f"?module={SHOPEE_DOC_MODULE}&type=1"
    )

def list_api_names() -> list[str]:
    return sorted(ACCOUNT_HEALTH_ENDPOINTS.keys())
