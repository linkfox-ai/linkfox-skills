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

import json
import sys
from typing import Any, Dict
from urllib.parse import quote

from _spapi_orders_common import (
    developer_proxy_call,
    emit_result,
    ensure_auth_skill_available,
    get_store_tokens,
    lf_inline_flag,
)

SHIPMENT_STATUSES = frozenset({"ReadyForPickup", "PickedUp", "RefusedPickup"})


def _path(order_id: str) -> str:
    oid = quote(str(order_id).strip(), safe="")
    return f"orders/v0/orders/{oid}/shipment"


def _build_body(params: dict) -> Dict[str, Any]:
    mid = params.get("marketplaceId")
    st = params.get("shipmentStatus")
    if not mid or not st:
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
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available("update_shipment_status.py")

    for f in ("sellerId", "region", "orderId"):
        if f not in params:
            print(f"Missing required field: {f}", file=sys.stderr)
            sys.exit(1)

    path = _path(params["orderId"])
    body_obj = _build_body(params)
    body_str = json.dumps(body_obj, ensure_ascii=False)

    tokens = get_store_tokens(str(params["sellerId"]), str(params["region"]))
    if "error" in tokens or "accessToken" not in tokens:
        print(json.dumps(tokens, indent=2, ensure_ascii=False))
        sys.exit(1)

    proxy = developer_proxy_call(
        str(params["region"]),
        path,
        "POST",
        tokens["accessToken"],
        body=body_str,
    )
    out: dict = {
        "developerProxy": proxy,
        "resolvedPath": path,
        "requestBody": body_obj,
    }
    inline = lf_inline_flag()
    emit_result(out, inline)


if __name__ == "__main__":
    main()
