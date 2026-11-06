#!/usr/bin/env python3
"""
Amazon Store — batchInventory (External Fulfillment Inventory v2024-09-11)
=========================================================================

POST `externalFulfillment/inventory/2024-09-11/inventories`。
默认简化入参：requests 每项含 action=fetch|update、locationId、skuId；
update 另需 quantity，可选 clientSequenceNumber / marketplaceAttributes。
高级：useAmazonRequestShape=true 时直接传 Amazon 原始 requests（1～10 条）。

官方参考: https://developer-docs.amazon.com/sp-api/reference/batchinventory
"""

from __future__ import annotations

import json
import sys
from urllib.parse import urlencode

from _spapi_ef_common import (
    PATH_INVENTORY_BATCH,
    run_proxy,
    ensure_auth_skill_available,
    load_params_or_exit,
    require_fields,
)

MAX_REQUESTS = 10


def _expand_simple(req: dict) -> dict:
    action = str(req.get("action") or "").strip().lower()
    if action not in ("fetch", "update"):
        raise ValueError("each request needs action: fetch|update")
    location_id = str(req.get("locationId") or "").strip()
    sku_id = str(req.get("skuId") or "").strip()
    if not location_id or not sku_id:
        raise ValueError("each request needs locationId and skuId")

    qs = urlencode({"locationId": location_id, "skuId": sku_id})
    op = "fetch" if action == "fetch" else "update"
    uri = f"/inventory/{op}?{qs}"

    body: dict = {}
    if req.get("marketplaceAttributes") is not None:
        body["marketplaceAttributes"] = req["marketplaceAttributes"]
    if action == "update":
        if "quantity" not in req:
            raise ValueError("update requests need quantity")
        body["quantity"] = req["quantity"]
        if req.get("clientSequenceNumber") is not None:
            body["clientSequenceNumber"] = req["clientSequenceNumber"]
    elif req.get("clientSequenceNumber") is not None:
        body["clientSequenceNumber"] = req["clientSequenceNumber"]

    # Official examples use method POST for both fetch and update sub-ops.
    out: dict = {"method": "POST", "uri": uri}
    if body:
        out["body"] = body
    return out


def main() -> None:
    params = load_params_or_exit(
        "Usage: post_batch_inventory.py '<JSON>'\n"
        f"Required: sellerId, region, requests (1..{MAX_REQUESTS}).\n"
        "Simple item: action(fetch|update), locationId, skuId [, quantity, "
        "clientSequenceNumber, marketplaceAttributes].\n"
        "Or useAmazonRequestShape:true with Amazon raw requests."
    )
    if not params.get("skipDepCheck"):
        ensure_auth_skill_available("post_batch_inventory.py")
    require_fields(params, ["sellerId", "region", "requests"])

    requests = params["requests"]
    if not isinstance(requests, list) or not (1 <= len(requests) <= MAX_REQUESTS):
        print(f"requests must be a list of 1..{MAX_REQUESTS} items", file=sys.stderr)
        sys.exit(1)
    if any(not isinstance(item, dict) for item in requests):
        print("requests 中每一项必须是 JSON 对象", file=sys.stderr)
        sys.exit(1)

    use_raw = bool(params.get("useAmazonRequestShape"))
    try:
        amazon_requests = requests if use_raw else [_expand_simple(r) for r in requests]
    except (ValueError, TypeError, KeyError) as e:
        print(f"Invalid request item: {e}", file=sys.stderr)
        sys.exit(1)

    body_obj = {"requests": amazon_requests}
    body_str = json.dumps(body_obj, ensure_ascii=False)
    run_proxy(str(params['region']), PATH_INVENTORY_BATCH, 'POST', str(params['sellerId']), body=body_str, result_field='batchInventory', operation='post_batch_inventory', ok_statuses=(200, 207), output_fields={'requestBody': body_obj})


if __name__ == "__main__":
    main()
