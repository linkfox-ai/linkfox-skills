#!/usr/bin/env python3
"""
Amazon Store — searchOrders (SP-API Orders v2026-01-01)
=======================================================

GET `orders/2026-01-01/orders`，按创建或更新时间窗检索订单。

官方参考: https://developer-docs.amazon.com/sp-api/reference/searchorders

Usage:
  python search_orders.py '{
    "sellerId":"A1...",
    "region":"NA",
    "marketplaceIds":["ATVPDKIKX0DER"],
    "lastUpdatedAfter":"2026-05-01T00:00:00Z"
  }'

必须二选一：createdAfter **或** lastUpdatedAfter（不可同时传另一组时间字段，规则见官方文档）。
可选：createdBefore、lastUpdatedBefore、fulfillmentStatuses、fulfilledBy、maxResultsPerPage、
paginationToken（上一页响应中的 nextToken）、includedData、skipDepCheck
"""

from __future__ import annotations

import sys
from typing import List
from urllib.parse import quote

from _spapi_orders_common import run_proxy, ensure_auth_skill_available, load_cli_params, require_fields

PATH = "orders/2026-01-01/orders"


def _str_list(val: object, name: str) -> List[str]:
    if val is None:
        return []
    if isinstance(val, str):
        return [x.strip() for x in val.split(",") if x.strip()]
    if isinstance(val, list):
        return [str(x).strip() for x in val if str(x).strip()]
    print(f"{name} must be string or string[]", file=sys.stderr)
    sys.exit(1)


def _build_query(p: dict) -> str:
    ca = p.get("createdAfter")
    cb = p.get("createdBefore")
    lua = p.get("lastUpdatedAfter")
    lub = p.get("lastUpdatedBefore")
    if ca and lua:
        print("Provide only one of createdAfter or lastUpdatedAfter.", file=sys.stderr)
        sys.exit(1)
    if not ca and not lua:
        print("Required: createdAfter OR lastUpdatedAfter (ISO 8601).", file=sys.stderr)
        sys.exit(1)
    if ca and (lua or lub):
        print("When using createdAfter, do not use lastUpdatedAfter/lastUpdatedBefore.", file=sys.stderr)
        sys.exit(1)
    if lua and (ca or cb):
        print("When using lastUpdatedAfter, do not use createdAfter/createdBefore.", file=sys.stderr)
        sys.exit(1)

    parts: list[str] = []

    def add(k: str, v: str) -> None:
        parts.append(f"{k}={quote(v, safe='')}")

    if ca:
        add("createdAfter", str(ca).strip())
    if cb:
        add("createdBefore", str(cb).strip())
    if lua:
        add("lastUpdatedAfter", str(lua).strip())
    if lub:
        add("lastUpdatedBefore", str(lub).strip())

    marketplaces = _str_list(p.get("marketplaceIds"), "marketplaceIds")
    if not 1 <= len(marketplaces) <= 50:
        print("marketplaceIds 必须包含 1～50 个站点 ID。", file=sys.stderr)
        raise SystemExit(1)
    for mid in marketplaces:
        add("marketplaceIds", mid)
    for fs in _str_list(p.get("fulfillmentStatuses"), "fulfillmentStatuses"):
        add("fulfillmentStatuses", fs)
    for fb in _str_list(p.get("fulfilledBy"), "fulfilledBy"):
        add("fulfilledBy", fb)
    for inc in _str_list(p.get("includedData"), "includedData"):
        add("includedData", inc)

    mrp = p.get("maxResultsPerPage")
    if mrp is not None:
        try:
            page_size = int(mrp)
        except (TypeError, ValueError, OverflowError):
            print("maxResultsPerPage 必须为 1～100 的整数。", file=sys.stderr)
            raise SystemExit(1)
        if isinstance(mrp, bool) or not 1 <= page_size <= 100:
            print("maxResultsPerPage 必须为 1～100 的整数。", file=sys.stderr)
            raise SystemExit(1)
        add("maxResultsPerPage", str(page_size))

    pt = p.get("paginationToken")
    if pt:
        add("paginationToken", str(pt).strip())

    return "&".join(parts)


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: search_orders.py '<JSON>'\n"
            "Required: sellerId, region, marketplaceIds, "
            "and either createdAfter or lastUpdatedAfter.",
            file=sys.stderr,
        )
        sys.exit(1)
    params = load_cli_params()

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available("search_orders.py")

    require_fields(params, ("sellerId", "region", "marketplaceIds"))

    seller_id = str(params["sellerId"])
    region = str(params["region"])
    qs = _build_query(params)

    run_proxy("searchOrders", region, PATH, "GET", seller_id,
              query_string=qs, result_field="searchOrders")


if __name__ == "__main__":
    main()
