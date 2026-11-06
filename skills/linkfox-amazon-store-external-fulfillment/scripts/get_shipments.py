#!/usr/bin/env python3
"""
Amazon Store — getShipments (External Fulfillment Shipping v2024-09-11)
======================================================================

GET `externalFulfillment/2024-09-11/shipments`

官方参考: https://developer-docs.amazon.com/sp-api/reference/getshipments-1
"""

from __future__ import annotations


from _spapi_ef_common import (
    PATH_SHIPMENTS,
    build_query,
    run_proxy,
    ensure_auth_skill_available,
    load_params_or_exit,
    require_fields,
)


def main() -> None:
    params = load_params_or_exit(
        "Usage: get_shipments.py '<JSON>'\n"
        "Required: sellerId, region, status\n"
        "Optional: locationId, marketplaceId, channelName, lastUpdatedAfter, "
        "lastUpdatedBefore, maxResults, paginationToken"
    )
    if not params.get("skipDepCheck"):
        ensure_auth_skill_available("get_shipments.py")
    require_fields(params, ["sellerId", "region", "status"])

    qs = build_query(
        [
            ("status", params.get("status")),
            ("locationId", params.get("locationId")),
            ("marketplaceId", params.get("marketplaceId")),
            ("channelName", params.get("channelName")),
            ("lastUpdatedAfter", params.get("lastUpdatedAfter")),
            ("lastUpdatedBefore", params.get("lastUpdatedBefore")),
            ("maxResults", params.get("maxResults")),
            ("paginationToken", params.get("paginationToken")),
        ]
    )
    run_proxy(str(params['region']), PATH_SHIPMENTS, 'GET', str(params['sellerId']), query_string=qs, result_field='shipments', operation='get_shipments', output_fields={'queryString': qs})


if __name__ == "__main__":
    main()
