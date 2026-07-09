"""Shopee Payment module API registry (v2.payment.*)."""

from __future__ import annotations

from typing import Literal, TypedDict

SHOPEE_DOC_MODULE = "97"

class PaymentEndpoint(TypedDict, total=False):
    path: str
    method: Literal["GET", "POST"]
    response_key: str
    required: list[str]
    body_fields: list[str]
    notes: str

PAYMENT_ENDPOINTS: dict[str, PaymentEndpoint] = {
    "get_escrow_detail": {
        "path": "api/v2/payment/get_escrow_detail",
        "method": "GET",
        "response_key": "getEscrowDetail",
        "required": ['order_sn'],
        "notes": 'Escrow/settlement detail for order',
    },
    "set_shop_installment_status": {
        "path": "api/v2/payment/set_shop_installment_status",
        "method": "POST",
        "response_key": "setShopInstallmentStatus",
        "notes": 'Enable/disable shop installment; pass body',
    },
    "get_shop_installment_status": {
        "path": "api/v2/payment/get_shop_installment_status",
        "method": "GET",
        "response_key": "getShopInstallmentStatus",
        "notes": 'Shop installment status',
    },
    "get_payout_detail": {
        "path": "api/v2/payment/get_payout_detail",
        "method": "GET",
        "response_key": "getPayoutDetail",
        "notes": 'Payout detail; optional payout_time_from/to',
    },
    "set_item_installment_status": {
        "path": "api/v2/payment/set_item_installment_status",
        "method": "POST",
        "response_key": "setItemInstallmentStatus",
        "notes": 'Set item installment status; pass body',
    },
    "get_item_installment_status": {
        "path": "api/v2/payment/get_item_installment_status",
        "method": "GET",
        "response_key": "getItemInstallmentStatus",
        "notes": 'Item installment status',
    },
    "get_payment_method_list": {
        "path": "api/v2/payment/get_payment_method_list",
        "method": "GET",
        "response_key": "getPaymentMethodList",
        "notes": 'Available payment methods',
    },
    "get_wallet_transaction_list": {
        "path": "api/v2/payment/get_wallet_transaction_list",
        "method": "GET",
        "response_key": "getWalletTransactionList",
        "notes": 'Wallet transactions; pagination/time filters',
    },
    "get_escrow_list": {
        "path": "api/v2/payment/get_escrow_list",
        "method": "GET",
        "response_key": "getEscrowList",
        "notes": 'Escrow list; time range filters',
    },
    "get_payout_info": {
        "path": "api/v2/payment/get_payout_info",
        "method": "GET",
        "response_key": "getPayoutInfo",
        "notes": 'Payout summary info',
    },
    "get_billing_transaction_info": {
        "path": "api/v2/payment/get_billing_transaction_info",
        "method": "GET",
        "response_key": "getBillingTransactionInfo",
        "notes": 'Billing transaction info',
    },
    "get_escrow_detail_batch": {
        "path": "api/v2/payment/get_escrow_detail_batch",
        "method": "POST",
        "response_key": "getEscrowDetailBatch",
        "notes": 'Batch escrow detail; pass body with order_sn_list',
    },
    "generate_income_statement": {
        "path": "api/v2/payment/generate_income_statement",
        "method": "POST",
        "response_key": "generateIncomeStatement",
        "notes": 'Generate income statement async',
    },
    "get_income_statement": {
        "path": "api/v2/payment/get_income_statement",
        "method": "GET",
        "response_key": "getIncomeStatement",
        "notes": 'Get generated income statement',
    },
    "generate_income_report": {
        "path": "api/v2/payment/generate_income_report",
        "method": "POST",
        "response_key": "generateIncomeReport",
        "notes": 'Generate income report async',
    },
    "get_income_report": {
        "path": "api/v2/payment/get_income_report",
        "method": "GET",
        "response_key": "getIncomeReport",
        "notes": 'Get generated income report',
    },
    "get_income_overview": {
        "path": "api/v2/payment/get_income_overview",
        "method": "GET",
        "response_key": "getIncomeOverview",
        "notes": 'Income overview/summary',
    },
    "get_income_detail": {
        "path": "api/v2/payment/get_income_detail",
        "method": "GET",
        "response_key": "getIncomeDetail",
        "notes": 'Income detail breakdown',
    },
}

RESERVED_PARAM_KEYS = frozenset({
    "shopId", "merchantId", "skipDepCheck", "body", "requestBody", "api", "contentType",
})

LIST_QUERY_FIELDS = frozenset()

def official_doc_url(api_name: str) -> str:
    return (
        f"https://open.shopee.com/documents/v2/v2.payment.{api_name}"
        f"?module={SHOPEE_DOC_MODULE}&type=1"
    )

def list_api_names() -> list[str]:
    return sorted(PAYMENT_ENDPOINTS.keys())
