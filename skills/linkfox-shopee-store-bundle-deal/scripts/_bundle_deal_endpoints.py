"""Shopee Bundle Deal 模块操作注册表（v2.bundle_deal.*）。"""

from __future__ import annotations

from typing import Literal, TypedDict


class BundleDealEndpoint(TypedDict, total=False):
    path: str
    method: Literal["GET", "POST"]
    response_key: str
    required: list[str]
    body_fields: list[str]
    notes: str

BUNDLE_DEAL_ENDPOINTS: dict[str, BundleDealEndpoint] = {
    "add_bundle_deal": {
        "path": "api/v2/bundle_deal/add_bundle_deal",
        "method": "POST",
        "response_key": "addBundleDeal",
        "notes": '创建套装优惠；传入完整请求体',
    },
    "add_bundle_deal_item": {
        "path": "api/v2/bundle_deal/add_bundle_deal_item",
        "method": "POST",
        "response_key": "addBundleDealItem",
        "notes": '添加参与套装优惠的商品',
    },
    "get_bundle_deal_list": {
        "path": "api/v2/bundle_deal/get_bundle_deal_list",
        "method": "GET",
        "response_key": "getBundleDealList",
        "notes": '查询套装优惠列表；支持分页和状态筛选',
    },
    "get_bundle_deal": {
        "path": "api/v2/bundle_deal/get_bundle_deal",
        "method": "GET",
        "response_key": "getBundleDeal",
        "notes": '按 bundle_deal_id 查询活动详情',
    },
    "get_bundle_deal_item": {
        "path": "api/v2/bundle_deal/get_bundle_deal_item",
        "method": "GET",
        "response_key": "getBundleDealItem",
        "notes": '查询活动内商品',
    },
    "update_bundle_deal": {
        "path": "api/v2/bundle_deal/update_bundle_deal",
        "method": "POST",
        "response_key": "updateBundleDeal",
        "notes": '更新套装优惠设置',
    },
    "update_bundle_deal_item": {
        "path": "api/v2/bundle_deal/update_bundle_deal_item",
        "method": "POST",
        "response_key": "updateBundleDealItem",
        "notes": '更新活动商品设置',
    },
    "end_bundle_deal": {
        "path": "api/v2/bundle_deal/end_bundle_deal",
        "method": "POST",
        "response_key": "endBundleDeal",
        "notes": '提前结束套装优惠',
    },
    "delete_bundle_deal": {
        "path": "api/v2/bundle_deal/delete_bundle_deal",
        "method": "POST",
        "response_key": "deleteBundleDeal",
        "notes": '删除套装优惠',
    },
    "delete_bundle_deal_item": {
        "path": "api/v2/bundle_deal/delete_bundle_deal_item",
        "method": "POST",
        "response_key": "deleteBundleDealItem",
        "notes": '移除活动商品',
    },
}

RESERVED_PARAM_KEYS = frozenset({
    "shopId", "merchantId", "skipDepCheck", "body", "requestBody", "api", "contentType",
})

LIST_QUERY_FIELDS = frozenset()


