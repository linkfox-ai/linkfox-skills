#!/usr/bin/env python3
"""
Amazon Store — getOrderItemsBuyerInfo (SP-API Orders v0, deprecated)
===================================================================

GET `orders/v0/orders/{orderId}/orderItems/buyerInfo`，可选 NextToken。

官方参考: https://developer-docs.amazon.com/sp-api/reference/getorderitemsbuyerinfo
"""

from __future__ import annotations

import sys
from urllib.parse import quote

from _spapi_orders_common import run_proxy, ensure_auth_skill_available, load_cli_params, require_fields


def _path(order_id: str) -> str:
    oid = quote(str(order_id).strip(), safe="")
    return f"orders/v0/orders/{oid}/orderItems/buyerInfo"


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: get_order_items_buyer_info.py '<JSON>'\n"
            "Required: sellerId, region, orderId\nOptional: nextToken",
            file=sys.stderr,
        )
        sys.exit(1)
    params = load_cli_params()

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available("get_order_items_buyer_info.py")

    require_fields(params, ("sellerId", "region", "orderId"))

    path = _path(params["orderId"])
    qs = None
    nt = params.get("nextToken")
    if nt:
        qs = f"NextToken={quote(str(nt).strip(), safe='')}"

    run_proxy("getOrderItemsBuyerInfo", str(params["region"]), path, "GET", str(params["sellerId"]),
              query_string=qs, result_field="orderItemsBuyerInfo")


if __name__ == "__main__":
    main()
