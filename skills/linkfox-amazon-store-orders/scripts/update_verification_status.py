#!/usr/bin/env python3
"""
Amazon Store — updateVerificationStatus (SP-API Orders v0)
===========================================================

PATCH `orders/v0/orders/{orderId}/regulatedInfo`，批准或拒绝管制订单核验状态。

请求体须包含 regulatedOrderVerificationStatus 对象（结构以官方 schema 为准）。

官方参考: https://developer-docs.amazon.com/sp-api/reference/updateverificationstatus
"""

from __future__ import annotations

import sys
from typing import Any, Dict
from urllib.parse import quote

from _spapi_orders_common import run_proxy, ensure_auth_skill_available, load_cli_params, require_fields


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
    params = load_cli_params()

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available("update_verification_status.py")

    require_fields(params, ("sellerId", "region", "orderId"))

    body_obj: Dict[str, Any]
    if "requestBody" in params and isinstance(params["requestBody"], dict):
        body_obj = params["requestBody"]
    elif "regulatedOrderVerificationStatus" in params:
        if not isinstance(params["regulatedOrderVerificationStatus"], dict):
            print("regulatedOrderVerificationStatus 必须为 JSON 对象。", file=sys.stderr)
            sys.exit(1)
        body_obj = {"regulatedOrderVerificationStatus": params["regulatedOrderVerificationStatus"]}
    else:
        print("Provide regulatedOrderVerificationStatus or requestBody object.", file=sys.stderr)
        sys.exit(1)

    path = _path(params["orderId"])

    run_proxy("updateVerificationStatus", str(params["region"]), path, "PATCH", str(params["sellerId"]),
              body_obj=body_obj)


if __name__ == "__main__":
    main()
