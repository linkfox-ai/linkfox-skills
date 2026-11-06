"""Shopee 账户健康操作注册表（v2.account_health.*）。"""

from __future__ import annotations

from typing import Literal, TypedDict


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
        "notes": '店铺绩效指标与健康总览',
    },
    "get_metric_source_detail": {
        "path": "api/v2/account_health/get_metric_source_detail",
        "method": "GET",
        "response_key": "getMetricSourceDetail",
        "required": ["metric_id"],
        "notes": '按 metric_id 查询指标来源明细',
    },
    "get_penalty_point_history": {
        "path": "api/v2/account_health/get_penalty_point_history",
        "method": "GET",
        "response_key": "getPenaltyPointHistory",
        "notes": '扣分历史，支持分页和筛选',
    },
    "get_punishment_history": {
        "path": "api/v2/account_health/get_punishment_history",
        "method": "GET",
        "response_key": "getPunishmentHistory",
        "required": ["punishment_status"],
        "notes": '处罚历史，支持分页和筛选',
    },
    "get_listings_with_issues": {
        "path": "api/v2/account_health/get_listings_with_issues",
        "method": "GET",
        "response_key": "getListingsWithIssues",
        "notes": '存在健康问题的商品刊登',
    },
    "get_late_orders": {
        "path": "api/v2/account_health/get_late_orders",
        "method": "GET",
        "response_key": "getLateOrders",
        "notes": '需要处理的逾期订单，使用 page_no/page_size 分页',
    },
}

RESERVED_PARAM_KEYS = frozenset({
    "shopId", "merchantId", "skipDepCheck", "body", "requestBody", "api", "contentType", "accessToken",
})

LIST_QUERY_FIELDS = frozenset()


