"""Shopee Order module API registry (v2.order.*)."""

from __future__ import annotations

from typing import Any, Literal, TypedDict


class OrderEndpoint(TypedDict, total=False):
    path: str
    method: Literal["GET", "POST"]
    response_key: str
    required: list[str]
    body_fields: list[str]
    body_nested_keys: list[str]
    notes: str


ORDER_ENDPOINTS: dict[str, OrderEndpoint] = {
    "get_order_list": {
        "path": "api/v2/order/get_order_list",
        "method": "GET",
        "response_key": "getOrderList",
        "required": ["time_range_field", "time_from", "time_to", "page_size"],
        "notes": "time_from/time_to max 15 days; order_status optional filter",
    },
    "get_order_detail": {
        "path": "api/v2/order/get_order_detail",
        "method": "GET",
        "response_key": "getOrderDetail",
        "required": ["order_sn_list"],
        "notes": "order_sn_list: string or array, max 50, comma-joined",
    },
    "get_shipment_list": {
        "path": "api/v2/order/get_shipment_list",
        "method": "GET",
        "response_key": "getShipmentList",
        "required": ["page_size"],
        "notes": "READY_TO_SHIP orders eligible for shipping",
    },
    "search_package_list": {
        "path": "api/v2/order/search_package_list",
        "method": "POST",
        "response_key": "searchPackageList",
        "body_nested_keys": ["filter", "pagination", "sort"],
        "notes": "Pass body object or top-level filter/pagination/sort",
    },
    "get_package_detail": {
        "path": "api/v2/order/get_package_detail",
        "method": "GET",
        "response_key": "getPackageDetail",
        "required": ["package_number_list"],
        "notes": "package_number_list: comma-separated, max 50",
    },
    "split_order": {
        "path": "api/v2/order/split_order",
        "method": "POST",
        "response_key": "splitOrder",
        "required": ["order_sn", "package_list"],
        "body_fields": ["order_sn", "package_list"],
    },
    "unsplit_order": {
        "path": "api/v2/order/unsplit_order",
        "method": "POST",
        "response_key": "unsplitOrder",
        "required": ["order_sn"],
        "body_fields": ["order_sn"],
    },
    "cancel_order": {
        "path": "api/v2/order/cancel_order",
        "method": "POST",
        "response_key": "cancelOrder",
        "required": ["order_sn", "cancel_reason"],
        "body_fields": ["order_sn", "cancel_reason", "item_list", "partial_cancel_item_list"],
        "notes": "cancel_reason: OUT_OF_STOCK/CUSTOMER_REQUEST/UNDELIVERABLE_AREA/COD_NOT_SUPPORTED",
    },
    "handle_buyer_cancellation": {
        "path": "api/v2/order/handle_buyer_cancellation",
        "method": "POST",
        "response_key": "handleBuyerCancellation",
        "required": ["order_sn", "operation"],
        "body_fields": ["order_sn", "operation"],
        "notes": "operation: ACCEPT | REJECT",
    },
    "set_note": {
        "path": "api/v2/order/set_note",
        "method": "POST",
        "response_key": "setNote",
        "required": ["order_sn", "note"],
        "body_fields": ["order_sn", "note"],
    },
    "get_pending_buyer_invoice_order_list": {
        "path": "api/v2/order/get_pending_buyer_invoice_order_list",
        "method": "GET",
        "response_key": "getPendingBuyerInvoiceOrderList",
        "required": ["page_size"],
        "notes": "PH/BR local sellers",
    },
    "get_buyer_invoice_info": {
        "path": "api/v2/order/get_buyer_invoice_info",
        "method": "POST",
        "response_key": "getBuyerInvoiceInfo",
        "required": ["queries"],
        "body_fields": ["queries"],
        "notes": "VN/TH/PH local sellers",
    },
    "upload_invoice_doc": {
        "path": "api/v2/order/upload_invoice_doc",
        "method": "POST",
        "response_key": "uploadInvoiceDoc",
        "notes": "Official API uses multipart/form-data; pass full body via body key if gateway supports it. PH/BR.",
    },
    "download_invoice_doc": {
        "path": "api/v2/order/download_invoice_doc",
        "method": "GET",
        "response_key": "downloadInvoiceDoc",
        "required": ["order_sn"],
        "notes": "PH/BR",
    },
    "handle_prescription_check": {
        "path": "api/v2/order/handle_prescription_check",
        "method": "POST",
        "response_key": "handlePrescriptionCheck",
        "required": ["package_number", "operation"],
        "body_fields": [
            "package_number",
            "order_sn",
            "operation",
            "reject_reason",
            "is_approved",
            "reject_reason_code",
            "items",
            "pharmacist_name",
            "free_text",
        ],
        "notes": "operation: APPROVE | REJECT; ID/PH whitelist",
    },
    "get_warehouse_filter_config": {
        "path": "api/v2/order/get_warehouse_filter_config",
        "method": "GET",
        "response_key": "getWarehouseFilterConfig",
        "notes": "Multi-warehouse shops",
    },
    "get_booking_list": {
        "path": "api/v2/order/get_booking_list",
        "method": "GET",
        "response_key": "getBookingList",
        "required": ["time_range_field", "time_from", "time_to", "page_size"],
        "notes": "booking_status optional: READY_TO_SHIP/PROCESSED/SHIPPED/CANCELLED/MATCHED",
    },
    "get_booking_detail": {
        "path": "api/v2/order/get_booking_detail",
        "method": "GET",
        "response_key": "getBookingDetail",
        "required": ["booking_sn_list"],
        "notes": "booking_sn_list: comma-separated, max 50",
    },
    "generate_fbs_invoices": {
        "path": "api/v2/order/generate_fbs_invoices",
        "method": "POST",
        "response_key": "generateFbsInvoices",
        "body_nested_keys": ["batch_download"],
        "body_fields": ["batch_download"],
        "notes": "BR FBS; batch_download.start/end YYYYMMDD",
    },
    "get_fbs_invoices_result": {
        "path": "api/v2/order/get_fbs_invoices_result",
        "method": "POST",
        "response_key": "getFbsInvoicesResult",
        "body_nested_keys": ["request_id_list"],
        "body_fields": ["request_id_list"],
    },
    "download_fbs_invoices": {
        "path": "api/v2/order/download_fbs_invoices",
        "method": "POST",
        "response_key": "downloadFbsInvoices",
        "body_nested_keys": ["request_id_list"],
        "body_fields": ["request_id_list"],
        "notes": "Download link expires in 30 minutes",
    },
    "get_estimiate_cancel_value": {
        "path": "api/v2/order/get_estimiate_cancel_value",
        "method": "POST",
        "response_key": "getEstimiateCancelValue",
        "required": ["order_sn", "partial_cancel_item_list"],
        "body_fields": ["order_sn", "partial_cancel_item_list"],
        "notes": "Official spelling: estimiate (not estimate)",
    },
}

RESERVED_PARAM_KEYS = frozenset({
    "shopId",
    "merchantId",
    "skipDepCheck",
    "body",
    "requestBody",
    "api",
    "contentType",
})

ORDER_STATUS_VALUES = frozenset({
    "UNPAID", "READY_TO_SHIP", "PROCESSED", "SHIPPED", "COMPLETED",
    "IN_CANCEL", "CANCELLED", "INVOICE_PENDING",
})


def official_doc_url(api_name: str) -> str:
    """Shopee Open Platform Order module doc URL (module=94)."""
    return (
        f"https://open.shopee.com/documents/v2/v2.order.{api_name}?module=94&type=1"
    )


def list_api_names() -> list[str]:
    return sorted(ORDER_ENDPOINTS.keys())
