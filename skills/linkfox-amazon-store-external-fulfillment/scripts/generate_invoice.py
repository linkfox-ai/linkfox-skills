#!/usr/bin/env python3
"""
Amazon Store — generateInvoice (External Fulfillment Shipping v2024-09-11)
=========================================================================

POST `externalFulfillment/2024-09-11/shipments/{shipmentId}/invoice`

官方参考: https://developer-docs.amazon.com/sp-api/reference/generateinvoice
"""

from __future__ import annotations


from _spapi_ef_common import (
    PATH_SHIPMENTS,
    run_proxy,
    enc_path_seg,
    ensure_auth_skill_available,
    load_params_or_exit,
    require_fields,
)


def main() -> None:
    params = load_params_or_exit(
        "Usage: generate_invoice.py '<JSON>'\nRequired: sellerId, region, shipmentId"
    )
    if not params.get("skipDepCheck"):
        ensure_auth_skill_available("generate_invoice.py")
    require_fields(params, ["sellerId", "region", "shipmentId"])

    path = f"{PATH_SHIPMENTS}/{enc_path_seg(params['shipmentId'])}/invoice"
    run_proxy(str(params['region']), path, 'POST', str(params['sellerId']), result_field='invoice', operation='generate_invoice')


if __name__ == "__main__":
    main()
