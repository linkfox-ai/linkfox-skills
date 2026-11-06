"""Shopee 退货退款操作注册表（v2.returns.*）。"""

from __future__ import annotations

from typing import Literal, TypedDict


class ReturnsEndpoint(TypedDict, total=False):
    path: str
    method: Literal["GET", "POST"]
    response_key: str
    required: list[str]
    body_fields: list[str]
    notes: str

RETURNS_ENDPOINTS: dict[str, ReturnsEndpoint] = {
    "get_return_list": {
        "path": "api/v2/returns/get_return_list",
        "method": "GET",
        "response_key": "getReturnList",
        "notes": '查询退货退款列表',
    },
    "get_return_detail": {
        "path": "api/v2/returns/get_return_detail",
        "method": "GET",
        "response_key": "getReturnDetail",
        "required": ['return_sn'],
        "notes": '查询退货退款详情',
    },
    "confirm": {
        "path": "api/v2/returns/confirm",
        "method": "POST",
        "response_key": "confirm",
        "notes": '确认退货',
    },
    "dispute": {
        "path": "api/v2/returns/dispute",
        "method": "POST",
        "response_key": "dispute",
        "notes": '发起退货争议',
    },
    "get_available_solutions": {
        "path": "api/v2/returns/get_available_solutions",
        "method": "GET",
        "response_key": "getAvailableSolutions",
        "required": ['return_sn'],
        "notes": '查询可用解决方案',
    },
    "offer": {
        "path": "api/v2/returns/offer",
        "method": "POST",
        "response_key": "offer",
        "notes": '提出解决方案',
    },
    "accept_offer": {
        "path": "api/v2/returns/accept_offer",
        "method": "POST",
        "response_key": "acceptOffer",
        "notes": '接受解决方案',
    },
    "convert_image": {
        "path": "api/v2/returns/convert_image",
        "method": "POST",
        "response_key": "convertImage",
        "notes": '转换凭证图片',
    },
    "upload_proof": {
        "path": "api/v2/returns/upload_proof",
        "method": "POST",
        "response_key": "uploadProof",
        "notes": '上传退货凭证',
    },
    "query_proof": {
        "path": "api/v2/returns/query_proof",
        "method": "GET",
        "response_key": "queryProof",
        "notes": '查询退货凭证',
    },
    "get_return_dispute_reason": {
        "path": "api/v2/returns/get_return_dispute_reason",
        "method": "GET",
        "response_key": "getReturnDisputeReason",
        "notes": '查询争议原因',
    },
    "cancel_dispute": {
        "path": "api/v2/returns/cancel_dispute",
        "method": "POST",
        "response_key": "cancelDispute",
        "notes": '取消退货争议',
    },
    "get_shipping_carrier": {
        "path": "api/v2/returns/get_shipping_carrier",
        "method": "GET",
        "response_key": "getShippingCarrier",
        "notes": '查询退货承运商',
    },
    "upload_shipping_proof": {
        "path": "api/v2/returns/upload_shipping_proof",
        "method": "POST",
        "response_key": "uploadShippingProof",
        "notes": '上传退货运单凭证',
    },
    "get_reverse_tracking_info": {
        "path": "api/v2/returns/get_reverse_tracking_info",
        "method": "GET",
        "response_key": "getReverseTrackingInfo",
        "notes": '查询逆向物流轨迹',
    },
}

RESERVED_PARAM_KEYS = frozenset({
    "shopId", "merchantId", "skipDepCheck", "body", "requestBody", "api", "contentType",
})

LIST_QUERY_FIELDS = frozenset()


