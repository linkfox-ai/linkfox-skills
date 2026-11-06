#!/usr/bin/env python3
"""
Amazon Store — getShipment (External Fulfillment Shipping v2024-09-11)
=====================================================================

GET `externalFulfillment/2024-09-11/shipments/{shipmentId}`

官方参考: https://developer-docs.amazon.com/sp-api/reference/getshipment-1
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
        "Usage: get_shipment.py '<JSON>'\nRequired: sellerId, region, shipmentId"
    )
    if not params.get("skipDepCheck"):
        ensure_auth_skill_available("get_shipment.py")
    require_fields(params, ["sellerId", "region", "shipmentId"])

    path = f"{PATH_SHIPMENTS}/{enc_path_seg(params['shipmentId'])}"
    run_proxy(str(params['region']), path, 'GET', str(params['sellerId']), result_field='shipment', operation='get_shipment')


if __name__ == "__main__":
    main()
