"""Shopee Voucher module API registry (v2.voucher.*)."""

from __future__ import annotations

from typing import Literal, TypedDict

SHOPEE_DOC_MODULE = "112"

class VoucherEndpoint(TypedDict, total=False):
    path: str
    method: Literal["GET", "POST"]
    response_key: str
    required: list[str]
    body_fields: list[str]
    notes: str

VOUCHER_ENDPOINTS: dict[str, VoucherEndpoint] = {
    "add_voucher": {
        "path": "api/v2/voucher/add_voucher",
        "method": "POST",
        "response_key": "addVoucher",
        "notes": 'Create shop voucher; pass full body',
    },
    "delete_voucher": {
        "path": "api/v2/voucher/delete_voucher",
        "method": "POST",
        "response_key": "deleteVoucher",
        "notes": 'Delete voucher',
    },
    "end_voucher": {
        "path": "api/v2/voucher/end_voucher",
        "method": "POST",
        "response_key": "endVoucher",
        "notes": 'End voucher early',
    },
    "update_voucher": {
        "path": "api/v2/voucher/update_voucher",
        "method": "POST",
        "response_key": "updateVoucher",
        "notes": 'Update voucher settings',
    },
    "get_voucher": {
        "path": "api/v2/voucher/get_voucher",
        "method": "GET",
        "response_key": "getVoucher",
        "notes": 'Voucher detail by voucher_id',
    },
    "get_voucher_list": {
        "path": "api/v2/voucher/get_voucher_list",
        "method": "GET",
        "response_key": "getVoucherList",
        "notes": 'List vouchers; pagination/status filters',
    },
}

RESERVED_PARAM_KEYS = frozenset({
    "shopId", "merchantId", "skipDepCheck", "body", "requestBody", "api", "contentType",
})

LIST_QUERY_FIELDS = frozenset()

def official_doc_url(api_name: str) -> str:
    return (
        f"https://open.shopee.com/documents/v2/v2.voucher.{api_name}"
        f"?module={SHOPEE_DOC_MODULE}&type=1"
    )

def list_api_names() -> list[str]:
    return sorted(VOUCHER_ENDPOINTS.keys())
