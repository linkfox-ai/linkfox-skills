#!/usr/bin/env python3
"""
Amazon Store — confirmShipment (SP-API Orders v0)
=================================================

POST `orders/v0/orders/{orderId}/shipmentConfirmation`，提交发货确认信息。

请将 Amazon 要求的完整 JSON 放在 **requestBody** 对象中（通常含 packageDetail 等字段），
脚本原样转发。

官方参考: https://developer-docs.amazon.com/sp-api/reference/confirmshipment
"""

from __future__ import annotations

import sys
from urllib.parse import quote

from _spapi_orders_common import run_proxy, ensure_auth_skill_available, load_cli_params, require_fields


def _path(order_id: str) -> str:
    oid = quote(str(order_id).strip(), safe="")
    return f"orders/v0/orders/{oid}/shipmentConfirmation"


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: confirm_shipment.py '<JSON>'\n"
            "Required: sellerId, region, orderId, requestBody (object per Amazon confirmShipment schema)",
            file=sys.stderr,
        )
        sys.exit(1)
    params = load_cli_params()

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available("confirm_shipment.py")

    require_fields(params, ("sellerId", "region", "orderId", "requestBody"))

    rb = params["requestBody"]
    if not isinstance(rb, dict):
        print("requestBody must be a JSON object.", file=sys.stderr)
        sys.exit(1)

    path = _path(params["orderId"])

    run_proxy("confirmShipment", str(params["region"]), path, "POST", str(params["sellerId"]),
              body_obj=rb)


if __name__ == "__main__":
    main()
