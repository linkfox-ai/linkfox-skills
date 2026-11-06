"""Shopee Merchant 模块接口注册表（v2.merchant.*）。"""

from __future__ import annotations

from typing import Literal, TypedDict


class MerchantEndpoint(TypedDict, total=False):
    path: str
    method: Literal["GET", "POST"]
    response_key: str
    required: list[str]
    body_fields: list[str]
    notes: str

MERCHANT_ENDPOINTS: dict[str, MerchantEndpoint] = {
    "get_merchant_info": {
        "path": "api/v2/merchant/get_merchant_info",
        "method": "GET",
        "response_key": "getMerchantInfo",
        "notes": '商户名称、区域、币种、授权和过期时间',
    },
    "get_shop_list_by_merchant": {
        "path": "api/v2/merchant/get_shop_list_by_merchant",
        "method": "GET",
        "response_key": "getShopListByMerchant",
        "required": ['page_no', 'page_size'],
        "notes": '商户绑定店铺；page_size 最大 500',
    },
    "get_merchant_warehouse_location_list": {
        "path": "api/v2/merchant/get_merchant_warehouse_location_list",
        "method": "GET",
        "response_key": "getMerchantWarehouseLocationList",
        "notes": '商户仓库位置',
    },
    "get_merchant_warehouse_list": {
        "path": "api/v2/merchant/get_merchant_warehouse_list",
        "method": "GET",
        "response_key": "getMerchantWarehouseList",
        "notes": '商户仓库列表',
    },
    "get_warehouse_eligible_shop_list": {
        "path": "api/v2/merchant/get_warehouse_eligible_shop_list",
        "method": "GET",
        "response_key": "getWarehouseEligibleShopList",
        "notes": '可使用仓库的店铺',
    },
    "get_merchant_prepaid_account_list": {
        "path": "api/v2/merchant/get_merchant_prepaid_account_list",
        "method": "GET",
        "response_key": "getMerchantPrepaidAccountList",
        "notes": '商户预付账户',
    },
}

RESERVED_PARAM_KEYS = frozenset({
    "shopId", "merchantId", "skipDepCheck", "body", "requestBody", "api", "contentType",
})

LIST_QUERY_FIELDS = frozenset()


def list_api_names() -> list[str]:
    return sorted(MERCHANT_ENDPOINTS.keys())
