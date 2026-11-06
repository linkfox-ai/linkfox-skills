#!/usr/bin/env python3
"""
Amazon Store — getOrderRegulatedInfo (SP-API Orders v0)
======================================================

GET `orders/v0/orders/{orderId}/regulatedInfo`（管制商品订单信息）。

官方参考: https://developer-docs.amazon.com/sp-api/reference/getorderregulatedinfo
"""

from __future__ import annotations

import sys
from urllib.parse import quote

from _spapi_orders_common import run_proxy, ensure_auth_skill_available, load_cli_params, require_fields


def _path(order_id: str) -> str:
    oid = quote(str(order_id).strip(), safe="")
    return f"orders/v0/orders/{oid}/regulatedInfo"


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: get_order_regulated_info.py '<JSON>'\nRequired: sellerId, region, orderId",
            file=sys.stderr,
        )
        sys.exit(1)
    params = load_cli_params()

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available("get_order_regulated_info.py")

    require_fields(params, ("sellerId", "region", "orderId"))

    path = _path(params["orderId"])
    run_proxy("getOrderRegulatedInfo", str(params["region"]), path, "GET", str(params["sellerId"]),
              result_field="regulatedOrder")


if __name__ == "__main__":
    main()
