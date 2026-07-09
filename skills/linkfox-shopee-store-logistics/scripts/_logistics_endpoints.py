"""Shopee Logistics module API registry (v2.logistics.*)."""

from __future__ import annotations

from typing import Literal, TypedDict

SHOPEE_DOC_MODULE = "95"

class LogisticsEndpoint(TypedDict, total=False):
    path: str
    method: Literal["GET", "POST"]
    response_key: str
    required: list[str]
    body_fields: list[str]
    notes: str

LOGISTICS_ENDPOINTS: dict[str, LogisticsEndpoint] = {
    "get_shipping_parameter": {
        "path": "api/v2/logistics/get_shipping_parameter",
        "method": "GET",
        "response_key": "getShippingParameter",
        "required": ['order_sn'],
        "notes": 'Pickup/dropoff info before ship_order',
    },
    "get_mass_shipping_parameter": {
        "path": "api/v2/logistics/get_mass_shipping_parameter",
        "method": "POST",
        "response_key": "getMassShippingParameter",
        "notes": 'Batch shipping parameters; pass body with order_list',
    },
    "ship_order": {
        "path": "api/v2/logistics/ship_order",
        "method": "POST",
        "response_key": "shipOrder",
        "notes": 'Ship order; pass full body (order_sn, package_number, pickup, etc.)',
    },
    "mass_ship_order": {
        "path": "api/v2/logistics/mass_ship_order",
        "method": "POST",
        "response_key": "massShipOrder",
        "notes": 'Batch ship orders',
    },
    "update_shipping_order": {
        "path": "api/v2/logistics/update_shipping_order",
        "method": "POST",
        "response_key": "updateShippingOrder",
        "notes": 'Update shipping info after ship',
    },
    "get_tracking_number": {
        "path": "api/v2/logistics/get_tracking_number",
        "method": "GET",
        "response_key": "getTrackingNumber",
        "required": ['order_sn'],
        "notes": 'Get tracking number for order',
    },
    "get_mass_tracking_number": {
        "path": "api/v2/logistics/get_mass_tracking_number",
        "method": "POST",
        "response_key": "getMassTrackingNumber",
        "notes": 'Batch get tracking numbers',
    },
    "get_shipping_document_parameter": {
        "path": "api/v2/logistics/get_shipping_document_parameter",
        "method": "GET",
        "response_key": "getShippingDocumentParameter",
        "required": ['order_sn'],
        "notes": 'Params for creating shipping label/doc',
    },
    "create_shipping_document": {
        "path": "api/v2/logistics/create_shipping_document",
        "method": "POST",
        "response_key": "createShippingDocument",
        "notes": 'Create shipping document/label',
    },
    "get_shipping_document_result": {
        "path": "api/v2/logistics/get_shipping_document_result",
        "method": "GET",
        "response_key": "getShippingDocumentResult",
        "notes": 'Document creation result',
    },
    "download_shipping_document": {
        "path": "api/v2/logistics/download_shipping_document",
        "method": "GET",
        "response_key": "downloadShippingDocument",
        "notes": 'Download shipping label PDF',
    },
    "get_shipping_document_data_info": {
        "path": "api/v2/logistics/get_shipping_document_data_info",
        "method": "GET",
        "response_key": "getShippingDocumentDataInfo",
        "notes": 'Shipping document data info',
    },
    "get_tracking_info": {
        "path": "api/v2/logistics/get_tracking_info",
        "method": "GET",
        "response_key": "getTrackingInfo",
        "notes": 'Logistics tracking info; order_sn + package_number',
    },
    "get_address_list": {
        "path": "api/v2/logistics/get_address_list",
        "method": "GET",
        "response_key": "getAddressList",
        "notes": 'Seller pickup/return addresses',
    },
    "set_address_config": {
        "path": "api/v2/logistics/set_address_config",
        "method": "POST",
        "response_key": "setAddressConfig",
        "notes": 'Set default address config',
    },
    "update_address": {
        "path": "api/v2/logistics/update_address",
        "method": "POST",
        "response_key": "updateAddress",
        "notes": 'Update pickup/return address',
    },
    "delete_address": {
        "path": "api/v2/logistics/delete_address",
        "method": "POST",
        "response_key": "deleteAddress",
        "notes": 'Delete address',
    },
    "get_channel_list": {
        "path": "api/v2/logistics/get_channel_list",
        "method": "GET",
        "response_key": "getChannelList",
        "notes": 'Available logistics channels',
    },
    "update_channel": {
        "path": "api/v2/logistics/update_channel",
        "method": "POST",
        "response_key": "updateChannel",
        "notes": 'Update channel settings',
    },
    "get_operating_hours": {
        "path": "api/v2/logistics/get_operating_hours",
        "method": "GET",
        "response_key": "getOperatingHours",
        "notes": 'Pickup operating hours',
    },
    "get_operating_hour_restrictions": {
        "path": "api/v2/logistics/get_operating_hour_restrictions",
        "method": "GET",
        "response_key": "getOperatingHourRestrictions",
        "notes": 'Operating hour restrictions',
    },
    "update_operating_hours": {
        "path": "api/v2/logistics/update_operating_hours",
        "method": "POST",
        "response_key": "updateOperatingHours",
        "notes": 'Update operating hours',
    },
    "delete_special_operating_hour": {
        "path": "api/v2/logistics/delete_special_operating_hour",
        "method": "POST",
        "response_key": "deleteSpecialOperatingHour",
        "notes": 'Delete special operating hour',
    },
    "batch_update_tpf_warehouse_tracking_status": {
        "path": "api/v2/logistics/batch_update_tpf_warehouse_tracking_status",
        "method": "POST",
        "response_key": "batchUpdateTpfWarehouseTrackingStatus",
        "notes": 'Batch update TPF warehouse tracking',
    },
    "batch_ship_order": {
        "path": "api/v2/logistics/batch_ship_order",
        "method": "POST",
        "response_key": "batchShipOrder",
        "notes": 'Batch ship orders',
    },
    "update_tracking_status": {
        "path": "api/v2/logistics/update_tracking_status",
        "method": "POST",
        "response_key": "updateTrackingStatus",
        "notes": 'Update tracking status',
    },
    "get_booking_shipping_parameter": {
        "path": "api/v2/logistics/get_booking_shipping_parameter",
        "method": "GET",
        "response_key": "getBookingShippingParameter",
        "notes": 'Booking shipment parameters',
    },
    "ship_booking": {
        "path": "api/v2/logistics/ship_booking",
        "method": "POST",
        "response_key": "shipBooking",
        "notes": 'Ship booking order',
    },
    "get_booking_tracking_number": {
        "path": "api/v2/logistics/get_booking_tracking_number",
        "method": "GET",
        "response_key": "getBookingTrackingNumber",
        "notes": 'Booking tracking number',
    },
    "get_booking_shipping_document_parameter": {
        "path": "api/v2/logistics/get_booking_shipping_document_parameter",
        "method": "GET",
        "response_key": "getBookingShippingDocumentParameter",
        "notes": 'Booking label parameters',
    },
    "create_booking_shipping_document": {
        "path": "api/v2/logistics/create_booking_shipping_document",
        "method": "POST",
        "response_key": "createBookingShippingDocument",
        "notes": 'Create booking shipping document',
    },
    "get_booking_shipping_document_result": {
        "path": "api/v2/logistics/get_booking_shipping_document_result",
        "method": "GET",
        "response_key": "getBookingShippingDocumentResult",
        "notes": 'Booking document result',
    },
    "download_booking_shipping_document": {
        "path": "api/v2/logistics/download_booking_shipping_document",
        "method": "GET",
        "response_key": "downloadBookingShippingDocument",
        "notes": 'Download booking label',
    },
    "get_booking_shipping_document_data_info": {
        "path": "api/v2/logistics/get_booking_shipping_document_data_info",
        "method": "GET",
        "response_key": "getBookingShippingDocumentDataInfo",
        "notes": 'Booking document data',
    },
    "get_booking_tracking_info": {
        "path": "api/v2/logistics/get_booking_tracking_info",
        "method": "GET",
        "response_key": "getBookingTrackingInfo",
        "notes": 'Booking tracking info',
    },
    "download_to_label": {
        "path": "api/v2/logistics/download_to_label",
        "method": "GET",
        "response_key": "downloadToLabel",
        "notes": 'Download TO label',
    },
    "create_shipping_document_job": {
        "path": "api/v2/logistics/create_shipping_document_job",
        "method": "POST",
        "response_key": "createShippingDocumentJob",
        "notes": 'Create async shipping document job',
    },
    "get_shipping_document_job_status": {
        "path": "api/v2/logistics/get_shipping_document_job_status",
        "method": "GET",
        "response_key": "getShippingDocumentJobStatus",
        "notes": 'Async job status',
    },
    "download_shipping_document_job": {
        "path": "api/v2/logistics/download_shipping_document_job",
        "method": "GET",
        "response_key": "downloadShippingDocumentJob",
        "notes": 'Download async job result',
    },
    "update_self_collection_order_logistics": {
        "path": "api/v2/logistics/update_self_collection_order_logistics",
        "method": "POST",
        "response_key": "updateSelfCollectionOrderLogistics",
        "notes": 'Self-collection order logistics',
    },
    "get_mart_packaging_info": {
        "path": "api/v2/logistics/get_mart_packaging_info",
        "method": "GET",
        "response_key": "getMartPackagingInfo",
        "notes": 'Mart packaging info',
    },
    "set_mart_packaging_info": {
        "path": "api/v2/logistics/set_mart_packaging_info",
        "method": "POST",
        "response_key": "setMartPackagingInfo",
        "notes": 'Set mart packaging info',
    },
    "upload_serviceable_polygon": {
        "path": "api/v2/logistics/upload_serviceable_polygon",
        "method": "POST",
        "response_key": "uploadServiceablePolygon",
        "notes": 'Upload serviceable delivery polygon',
    },
    "check_polygon_update_status": {
        "path": "api/v2/logistics/check_polygon_update_status",
        "method": "GET",
        "response_key": "checkPolygonUpdateStatus",
        "notes": 'Polygon upload status',
    },
    "get_pause_status": {
        "path": "api/v2/logistics/get_pause_status",
        "method": "GET",
        "response_key": "getPauseStatus",
        "notes": 'Logistics pause status',
    },
    "set_pause_status": {
        "path": "api/v2/logistics/set_pause_status",
        "method": "POST",
        "response_key": "setPauseStatus",
        "notes": 'Set logistics pause status',
    },
}

RESERVED_PARAM_KEYS = frozenset({
    "shopId", "merchantId", "skipDepCheck", "body", "requestBody", "api", "contentType",
})

LIST_QUERY_FIELDS = frozenset({
    "order_sn_list",
})

def official_doc_url(api_name: str) -> str:
    return (
        f"https://open.shopee.com/documents/v2/v2.logistics.{api_name}"
        f"?module={SHOPEE_DOC_MODULE}&type=1"
    )

def list_api_names() -> list[str]:
    return sorted(LOGISTICS_ENDPOINTS.keys())
