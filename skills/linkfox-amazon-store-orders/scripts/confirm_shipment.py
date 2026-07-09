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

import json
import sys
from typing import Dict
from urllib.parse import quote

from _spapi_orders_common import (
    developer_proxy_call,
    emit_result,
    ensure_auth_skill_available,
    get_store_tokens,
    lf_inline_flag,
)


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
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available("confirm_shipment.py")

    for f in ("sellerId", "region", "orderId", "requestBody"):
        if f not in params:
            print(f"Missing required field: {f}", file=sys.stderr)
            sys.exit(1)

    rb = params["requestBody"]
    if not isinstance(rb, dict):
        print("requestBody must be a JSON object.", file=sys.stderr)
        sys.exit(1)

    path = _path(params["orderId"])
    body_str = json.dumps(rb, ensure_ascii=False)

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
    out: dict = {"developerProxy": proxy, "resolvedPath": path, "requestBody": rb}
    inline = lf_inline_flag()
    emit_result(out, inline)


if __name__ == "__main__":
    main()
