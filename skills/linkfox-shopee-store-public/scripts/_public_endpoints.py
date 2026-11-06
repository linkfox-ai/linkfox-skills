"""Shopee Public 模块操作注册表（v2.public.*）。"""

from __future__ import annotations

from typing import Literal, TypedDict


class PublicEndpoint(TypedDict, total=False):
    path: str
    method: Literal["GET", "POST"]
    response_key: str
    required: list[str]
    body_fields: list[str]
    notes: str

PUBLIC_ENDPOINTS: dict[str, PublicEndpoint] = {
    "get_shops_by_partner": {
        "path": "api/v2/public/get_shops_by_partner",
        "method": "GET",
        "response_key": "getShopsByPartner",
        "notes": '查询 Partner 下已授权店铺',
    },
    "get_merchants_by_partner": {
        "path": "api/v2/public/get_merchants_by_partner",
        "method": "GET",
        "response_key": "getMerchantsByPartner",
        "notes": '查询 Partner 下已授权商户',
    },
    "get_access_token": {
        "path": "api/v2/public/get_access_token",
        "method": "POST",
        "response_key": "getAccessToken",
        "notes": '使用授权码交换 token，传完整正文',
    },
    "refresh_access_token": {
        "path": "api/v2/public/refresh_access_token",
        "method": "POST",
        "response_key": "refreshAccessToken",
        "notes": '刷新 access token，传完整正文',
    },
    "get_token_by_resend_code": {
        "path": "api/v2/public/get_token_by_resend_code",
        "method": "POST",
        "response_key": "getTokenByResendCode",
        "notes": '使用 resend code 获取 token，传完整正文',
    },
    "get_shopee_ip_ranges": {
        "path": "api/v2/public/get_shopee_ip_ranges",
        "method": "GET",
        "response_key": "getShopeeIpRanges",
        "notes": '查询用于白名单配置的 Shopee 开放平台 IP 段',
    },
}

RESERVED_PARAM_KEYS = frozenset({
    "shopId", "merchantId", "accessToken", "skipDepCheck", "body", "requestBody", "api", "contentType",
})

LIST_QUERY_FIELDS = frozenset()


