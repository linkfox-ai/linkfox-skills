#!/usr/bin/env python3
"""
Amazon Store — getOrder (SP-API Orders v2026-01-01)
==================================================

GET `orders/2026-01-01/orders/{orderId}`，可选 includedData 数据集。

官方参考: https://developer-docs.amazon.com/sp-api/reference/getorder-3
"""

from __future__ import annotations

import json
import sys
from typing import List
from urllib.parse import quote

from _spapi_orders_common import (
    developer_proxy_call,
    emit_result,
    ensure_auth_skill_available,
    get_store_tokens,
    lf_inline_flag,
    merge_json_body,
)


def _str_list(val: object, name: str) -> List[str]:
    if val is None:
        return []
    if isinstance(val, str):
        return [x.strip() for x in val.split(",") if x.strip()]
    if isinstance(val, list):
        return [str(x).strip() for x in val if str(x).strip()]
    print(f"{name} must be string or string[]", file=sys.stderr)
    sys.exit(1)


def _path(order_id: str) -> str:
    return f"orders/2026-01-01/orders/{quote(str(order_id).strip(), safe='')}"


def _query(included_data: List[str]) -> str | None:
    if not included_data:
        return None
    parts = [f"includedData={quote(x, safe='')}" for x in included_data]
    return "&".join(parts)


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: get_order.py '<JSON>'\n"
            'Required: sellerId, region, orderId\n'
            "Optional: includedData (e.g. BUYER,FULFILLMENT,PACKAGES), skipDepCheck",
            file=sys.stderr,
        )
        sys.exit(1)
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available("get_order.py")

    for f in ("sellerId", "region", "orderId"):
        if f not in params:
            print(f"Missing required field: {f}", file=sys.stderr)
            sys.exit(1)

    seller_id = str(params["sellerId"])
    region = str(params["region"])
    order_id = str(params["orderId"]).strip()
    path = _path(order_id)
    qs = _query(_str_list(params.get("includedData"), "includedData"))

    tokens = get_store_tokens(seller_id, region)
    if "error" in tokens or "accessToken" not in tokens:
        print(json.dumps(tokens, indent=2, ensure_ascii=False))
        sys.exit(1)

    proxy = developer_proxy_call(region, path, "GET", tokens["accessToken"], query_string=qs)
    out: dict = {"developerProxy": proxy, "resolvedPath": path, "queryString": qs}
    merge_json_body(out, proxy, "order")
    inline = lf_inline_flag()
    emit_result(out, inline)


if __name__ == "__main__":
    main()
