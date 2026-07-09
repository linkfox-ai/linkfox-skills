"""Shopee Add-On Deal module API registry (v2.add_on_deal.*)."""

from __future__ import annotations

from typing import Literal, TypedDict

SHOPEE_DOC_MODULE = "111"

class AddOnDealEndpoint(TypedDict, total=False):
    path: str
    method: Literal["GET", "POST"]
    response_key: str
    required: list[str]
    body_fields: list[str]
    notes: str

ADD_ON_DEAL_ENDPOINTS: dict[str, AddOnDealEndpoint] = {
    "add_add_on_deal": {
        "path": "api/v2/add_on_deal/add_add_on_deal",
        "method": "POST",
        "response_key": "addAddOnDeal",
        "notes": 'Create add-on deal promotion; pass full body',
    },
    "add_add_on_deal_main_item": {
        "path": "api/v2/add_on_deal/add_add_on_deal_main_item",
        "method": "POST",
        "response_key": "addAddOnDealMainItem",
        "notes": 'Add main item to add-on deal',
    },
    "add_add_on_deal_sub_item": {
        "path": "api/v2/add_on_deal/add_add_on_deal_sub_item",
        "method": "POST",
        "response_key": "addAddOnDealSubItem",
        "notes": 'Add sub item to add-on deal',
    },
    "delete_add_on_deal": {
        "path": "api/v2/add_on_deal/delete_add_on_deal",
        "method": "POST",
        "response_key": "deleteAddOnDeal",
        "notes": 'Delete add-on deal',
    },
    "delete_add_on_deal_main_item": {
        "path": "api/v2/add_on_deal/delete_add_on_deal_main_item",
        "method": "POST",
        "response_key": "deleteAddOnDealMainItem",
        "notes": 'Remove main item from add-on deal',
    },
    "delete_add_on_deal_sub_item": {
        "path": "api/v2/add_on_deal/delete_add_on_deal_sub_item",
        "method": "POST",
        "response_key": "deleteAddOnDealSubItem",
        "notes": 'Remove sub item from add-on deal',
    },
    "get_add_on_deal_list": {
        "path": "api/v2/add_on_deal/get_add_on_deal_list",
        "method": "GET",
        "response_key": "getAddOnDealList",
        "notes": 'List add-on deals; pagination/status filters',
    },
    "get_add_on_deal": {
        "path": "api/v2/add_on_deal/get_add_on_deal",
        "method": "GET",
        "response_key": "getAddOnDeal",
        "notes": 'Add-on deal detail by add_on_deal_id',
    },
    "get_add_on_deal_main_item": {
        "path": "api/v2/add_on_deal/get_add_on_deal_main_item",
        "method": "GET",
        "response_key": "getAddOnDealMainItem",
        "notes": 'Main items in add-on deal',
    },
    "get_add_on_deal_sub_item": {
        "path": "api/v2/add_on_deal/get_add_on_deal_sub_item",
        "method": "GET",
        "response_key": "getAddOnDealSubItem",
        "notes": 'Sub items in add-on deal',
    },
    "update_add_on_deal": {
        "path": "api/v2/add_on_deal/update_add_on_deal",
        "method": "POST",
        "response_key": "updateAddOnDeal",
        "notes": 'Update add-on deal settings',
    },
    "update_add_on_deal_main_item": {
        "path": "api/v2/add_on_deal/update_add_on_deal_main_item",
        "method": "POST",
        "response_key": "updateAddOnDealMainItem",
        "notes": 'Update add-on deal main item settings',
    },
    "update_add_on_deal_sub_item": {
        "path": "api/v2/add_on_deal/update_add_on_deal_sub_item",
        "method": "POST",
        "response_key": "updateAddOnDealSubItem",
        "notes": 'Update add-on deal sub item settings',
    },
    "end_add_on_deal": {
        "path": "api/v2/add_on_deal/end_add_on_deal",
        "method": "POST",
        "response_key": "endAddOnDeal",
        "notes": 'End add-on deal early',
    },
}

RESERVED_PARAM_KEYS = frozenset({
    "shopId", "merchantId", "skipDepCheck", "body", "requestBody", "api", "contentType",
})

LIST_QUERY_FIELDS = frozenset()

def official_doc_url(api_name: str) -> str:
    return (
        f"https://open.shopee.com/documents/v2/v2.add_on_deal.{api_name}"
        f"?module={SHOPEE_DOC_MODULE}&type=1"
    )

def list_api_names() -> list[str]:
    return sorted(ADD_ON_DEAL_ENDPOINTS.keys())
