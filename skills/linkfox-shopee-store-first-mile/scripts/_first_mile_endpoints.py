"""Shopee FirstMile module API registry (v2.first_mile.*)."""

from __future__ import annotations

from typing import Literal, TypedDict

SHOPEE_DOC_MODULE = "96"

class FirstMileEndpoint(TypedDict, total=False):
    path: str
    method: Literal["GET", "POST"]
    response_key: str
    required: list[str]
    body_fields: list[str]
    notes: str

FIRST_MILE_ENDPOINTS: dict[str, FirstMileEndpoint] = {
    "get_unbind_order_list": {
        "path": "api/v2/first_mile/get_unbind_order_list",
        "method": "GET",
        "response_key": "getUnbindOrderList",
        "notes": 'Orders not yet bound to first-mile tracking',
    },
    "get_detail": {
        "path": "api/v2/first_mile/get_detail",
        "method": "GET",
        "response_key": "getDetail",
        "notes": 'First-mile detail by tracking number or batch',
    },
    "generate_first_mile_tracking_number": {
        "path": "api/v2/first_mile/generate_first_mile_tracking_number",
        "method": "POST",
        "response_key": "generateFirstMileTrackingNumber",
        "notes": 'Generate first-mile tracking number; pass body',
    },
    "bind_first_mile_tracking_number": {
        "path": "api/v2/first_mile/bind_first_mile_tracking_number",
        "method": "POST",
        "response_key": "bindFirstMileTrackingNumber",
        "notes": 'Bind orders to first-mile tracking number',
    },
    "unbind_first_mile_tracking_number": {
        "path": "api/v2/first_mile/unbind_first_mile_tracking_number",
        "method": "POST",
        "response_key": "unbindFirstMileTrackingNumber",
        "notes": 'Unbind first-mile tracking number from orders',
    },
    "get_tracking_number_list": {
        "path": "api/v2/first_mile/get_tracking_number_list",
        "method": "GET",
        "response_key": "getTrackingNumberList",
        "notes": 'List first-mile tracking numbers',
    },
    "get_waybill": {
        "path": "api/v2/first_mile/get_waybill",
        "method": "GET",
        "response_key": "getWaybill",
        "notes": 'Get first-mile waybill',
    },
    "get_channel_list": {
        "path": "api/v2/first_mile/get_channel_list",
        "method": "GET",
        "response_key": "getChannelList",
        "notes": 'First-mile channel list',
    },
    "get_courier_delivery_channel_list": {
        "path": "api/v2/first_mile/get_courier_delivery_channel_list",
        "method": "GET",
        "response_key": "getCourierDeliveryChannelList",
        "notes": 'Courier delivery channel list',
    },
    "get_transit_warehouse_list": {
        "path": "api/v2/first_mile/get_transit_warehouse_list",
        "method": "GET",
        "response_key": "getTransitWarehouseList",
        "notes": 'Transit warehouse list',
    },
    "generate_and_bind_first_mile_tracking_number": {
        "path": "api/v2/first_mile/generate_and_bind_first_mile_tracking_number",
        "method": "POST",
        "response_key": "generateAndBindFirstMileTrackingNumber",
        "notes": 'Generate and bind tracking in one step',
    },
    "bind_courier_delivery_first_mile_tracking_number": {
        "path": "api/v2/first_mile/bind_courier_delivery_first_mile_tracking_number",
        "method": "POST",
        "response_key": "bindCourierDeliveryFirstMileTrackingNumber",
        "notes": 'Bind courier delivery first-mile tracking',
    },
    "unbind_first_mile_tracking_number_all": {
        "path": "api/v2/first_mile/unbind_first_mile_tracking_number_all",
        "method": "POST",
        "response_key": "unbindFirstMileTrackingNumberAll",
        "notes": 'Unbind all orders from tracking number',
    },
    "get_courier_delivery_detail": {
        "path": "api/v2/first_mile/get_courier_delivery_detail",
        "method": "GET",
        "response_key": "getCourierDeliveryDetail",
        "notes": 'Courier delivery first-mile detail',
    },
    "get_courier_delivery_waybill": {
        "path": "api/v2/first_mile/get_courier_delivery_waybill",
        "method": "GET",
        "response_key": "getCourierDeliveryWaybill",
        "notes": 'Courier delivery waybill',
    },
    "get_courier_delivery_tracking_number_list": {
        "path": "api/v2/first_mile/get_courier_delivery_tracking_number_list",
        "method": "GET",
        "response_key": "getCourierDeliveryTrackingNumberList",
        "notes": 'Courier delivery tracking number list',
    },
}

RESERVED_PARAM_KEYS = frozenset({
    "shopId", "merchantId", "skipDepCheck", "body", "requestBody", "api", "contentType",
})

LIST_QUERY_FIELDS = frozenset()

def official_doc_url(api_name: str) -> str:
    return (
        f"https://open.shopee.com/documents/v2/v2.first_mile.{api_name}"
        f"?module={SHOPEE_DOC_MODULE}&type=1"
    )

def list_api_names() -> list[str]:
    return sorted(FIRST_MILE_ENDPOINTS.keys())
