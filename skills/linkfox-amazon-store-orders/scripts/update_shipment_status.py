#!/usr/bin/env python3
"""
Amazon Store — updateShipmentStatus (SP-API Orders v0)
======================================================

POST `orders/v0/orders/{orderId}/shipment`，更新自提等场景的发货状态。

Body 必填字段：marketplaceId、shipmentStatus（ReadyForPickup | PickedUp | RefusedPickup）；
可选 orderItems（部分行更新时的行与数量）。

官方参考: https://developer-docs.amazon.com/sp-api/reference/updateshipmentstatus
"""

from __future__ import annotations

import sys
from typing import Any, Dict
from urllib.parse import quote

from _spapi_orders_common import run_proxy, ensure_auth_skill_available, load_cli_params, require_fields

SHIPMENT_STATUSES = frozenset({"ReadyForPickup", "PickedUp", "RefusedPickup"})


def _path(order_id: str) -> str:
    oid = quote(str(order_id).strip(), safe="")
    return f"orders/v0/orders/{oid}/shipment"


def _build_body(params: dict) -> Dict[str, Any]:
    mid = params.get("marketplaceId")
    st = params.get("shipmentStatus")
    if not mid or not str(mid).strip() or not st:
        print("Missing marketplaceId or shipmentStatus.", file=sys.stderr)
        sys.exit(1)
    st_s = str(st).strip()
    if st_s not in SHIPMENT_STATUSES:
        print(f"shipmentStatus must be one of: {sorted(SHIPMENT_STATUSES)}", file=sys.stderr)
        sys.exit(1)
    body: Dict[str, Any] = {"marketplaceId": str(mid).strip(), "shipmentStatus": st_s}
    oi = params.get("orderItems")
    if oi is not None:
        if not isinstance(oi, list):
            print("orderItems must be an array when provided.", file=sys.stderr)
            sys.exit(1)
        body["orderItems"] = oi
    return body


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: update_shipment_status.py '<JSON>'\n"
            "Required: sellerId, region, orderId, marketplaceId, shipmentStatus\n"
            "Optional: orderItems, skipDepCheck",
            file=sys.stderr,
        )
        sys.exit(1)
    params = load_cli_params()

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available("update_shipment_status.py")

    require_fields(params, ("sellerId", "region", "orderId"))

    path = _path(params["orderId"])
    body_obj = _build_body(params)

    run_proxy("updateShipmentStatus", str(params["region"]), path, "POST", str(params["sellerId"]),
              body_obj=body_obj)


if __name__ == "__main__":
    main()
