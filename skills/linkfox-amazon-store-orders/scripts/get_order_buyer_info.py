#!/usr/bin/env python3
"""
Amazon Store — getOrderBuyerInfo (SP-API Orders v0, deprecated)
================================================================

GET `orders/v0/orders/{orderId}/buyerInfo`。官方标注 deprecated；买家 PII 可能需 RDT，以 Amazon 为准。

官方参考: https://developer-docs.amazon.com/sp-api/reference/getorderbuyerinfo
"""

from __future__ import annotations

import sys
from urllib.parse import quote

from _spapi_orders_common import run_proxy, ensure_auth_skill_available, load_cli_params, require_fields


def _path(order_id: str) -> str:
    oid = quote(str(order_id).strip(), safe="")
    return f"orders/v0/orders/{oid}/buyerInfo"


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: get_order_buyer_info.py '<JSON>'\nRequired: sellerId, region, orderId",
            file=sys.stderr,
        )
        sys.exit(1)
    params = load_cli_params()

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available("get_order_buyer_info.py")

    require_fields(params, ("sellerId", "region", "orderId"))

    path = _path(params["orderId"])
    run_proxy("getOrderBuyerInfo", str(params["region"]), path, "GET", str(params["sellerId"]),
              result_field="buyerInfo")


if __name__ == "__main__":
    main()
