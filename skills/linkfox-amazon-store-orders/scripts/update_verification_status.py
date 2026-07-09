#!/usr/bin/env python3
"""
Amazon Store — updateVerificationStatus (SP-API Orders v0)
===========================================================

PATCH `orders/v0/orders/{orderId}/regulatedInfo`，批准或拒绝管制订单核验状态。

请求体须包含 regulatedOrderVerificationStatus 对象（结构以官方 schema 为准）。

官方参考: https://developer-docs.amazon.com/sp-api/reference/updateverificationstatus
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


def _path(order_id: str) -> str:
    oid = quote(str(order_id).strip(), safe="")
    return f"orders/v0/orders/{oid}/regulatedInfo"


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: update_verification_status.py '<JSON>'\n"
            "Required: sellerId, region, orderId, regulatedOrderVerificationStatus (object)\n"
            "Or pass full Amazon body as requestBody (object).",
            file=sys.stderr,
        )
        sys.exit(1)
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available("update_verification_status.py")

    for f in ("sellerId", "region", "orderId"):
        if f not in params:
            print(f"Missing required field: {f}", file=sys.stderr)
            sys.exit(1)

    body_obj: Dict[str, Any]
    if "requestBody" in params and isinstance(params["requestBody"], dict):
        body_obj = params["requestBody"]
    elif "regulatedOrderVerificationStatus" in params:
        body_obj = {"regulatedOrderVerificationStatus": params["regulatedOrderVerificationStatus"]}
    else:
        print("Provide regulatedOrderVerificationStatus or requestBody object.", file=sys.stderr)
        sys.exit(1)

    path = _path(params["orderId"])
    body_str = json.dumps(body_obj, ensure_ascii=False)

    tokens = get_store_tokens(str(params["sellerId"]), str(params["region"]))
    if "error" in tokens or "accessToken" not in tokens:
        print(json.dumps(tokens, indent=2, ensure_ascii=False))
        sys.exit(1)

    proxy = developer_proxy_call(
        str(params["region"]),
        path,
        "PATCH",
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
