#!/usr/bin/env python3
"""
Amazon Store — getOrderBuyerInfo (SP-API Orders v0, deprecated)
================================================================

GET `orders/v0/orders/{orderId}/buyerInfo`。官方标注 deprecated；买家 PII 可能需 RDT，以 Amazon 为准。

官方参考: https://developer-docs.amazon.com/sp-api/reference/getorderbuyerinfo
"""

from __future__ import annotations

import json
import sys
from urllib.parse import quote

from _spapi_orders_common import (
    developer_proxy_call,
    emit_result,
    ensure_auth_skill_available,
    get_store_tokens,
    lf_inline_flag,
    merge_json_body,
)


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
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available("get_order_buyer_info.py")

    for f in ("sellerId", "region", "orderId"):
        if f not in params:
            print(f"Missing required field: {f}", file=sys.stderr)
            sys.exit(1)

    path = _path(params["orderId"])
    tokens = get_store_tokens(str(params["sellerId"]), str(params["region"]))
    if "error" in tokens or "accessToken" not in tokens:
        print(json.dumps(tokens, indent=2, ensure_ascii=False))
        sys.exit(1)

    proxy = developer_proxy_call(str(params["region"]), path, "GET", tokens["accessToken"])
    out: dict = {"developerProxy": proxy, "resolvedPath": path}
    merge_json_body(out, proxy, "buyerInfo")
    inline = lf_inline_flag()
    emit_result(out, inline)


if __name__ == "__main__":
    main()
