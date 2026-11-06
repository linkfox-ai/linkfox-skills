#!/usr/bin/env python3
"""
Amazon Store — getOrder (SP-API Orders v2026-01-01)
==================================================

GET `orders/2026-01-01/orders/{orderId}`，可选 includedData 数据集。

官方参考: https://developer-docs.amazon.com/sp-api/reference/getorder-3
"""

from __future__ import annotations

import sys
from typing import List
from urllib.parse import quote

from _spapi_orders_common import run_proxy, ensure_auth_skill_available, load_cli_params, require_fields


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
    params = load_cli_params()

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available("get_order.py")

    require_fields(params, ("sellerId", "region", "orderId"))

    seller_id = str(params["sellerId"])
    region = str(params["region"])
    order_id = str(params["orderId"]).strip()
    path = _path(order_id)
    qs = _query(_str_list(params.get("includedData"), "includedData"))

    run_proxy("getOrder", region, path, "GET", seller_id,
              query_string=qs, result_field="order")


if __name__ == "__main__":
    main()
