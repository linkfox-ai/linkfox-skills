#!/usr/bin/env python3
"""
Amazon Store — getItemOffersBatch (SP-API Product Pricing v0)
=============================================================

POST 批量查询多个 ASIN 的 getItemOffers（每批 1～20 条子请求）。

官方参考: https://developer-docs.amazon.com/sp-api/reference/getitemoffersbatch

JSON 入参（简化）:
  sellerId, region,
  requests: [ { "asin", "marketplaceId", "itemCondition", "customerType"?, "headers"? }, ... ]

脚本将每条展开为 Amazon 所需的 uri（/products/pricing/v0/items/{Asin}/offers）、method GET、
MarketplaceId、ItemCondition 等。若需完全自定义子请求体，可传 useAmazonRequestShape: true，
此时 requests 须为 Amazon 原始对象数组（仍须 1～20 条）。
"""

from __future__ import annotations

import json
import sys
from urllib.parse import quote

from _spapi_pricing_common import (
    developer_proxy_post_json,
    emit_result,
    ensure_auth_skill_available,
    get_store_tokens,
    lf_inline_flag,
)

PATH_BATCH = "batches/products/pricing/v0/itemOffers"
MAX_REQUESTS = 20


def _expand_simple(req: dict) -> dict:
    asin = str(req["asin"]).strip()
    if not asin:
        raise ValueError("each request needs non-empty asin")
    mid = str(req.get("marketplaceId") or "").strip()
    if not mid:
        raise ValueError("each request needs marketplaceId")
    ic = str(req.get("itemCondition") or "").strip()
    if not ic:
        raise ValueError("each request needs itemCondition")
    uri = f"/products/pricing/v0/items/{quote(asin, safe='')}/offers"
    out: dict = {
        "uri": uri,
        "method": "GET",
        "MarketplaceId": mid,
        "ItemCondition": ic,
    }
    if req.get("customerType"):
        out["CustomerType"] = str(req["customerType"]).strip()
    if req.get("headers") is not None:
        out["headers"] = req["headers"]
    return out


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: post_item_offers_batch.py '<JSON>'\n"
            f"Required: sellerId, region, requests (1..{MAX_REQUESTS} items).\n"
            "Each item: asin, marketplaceId, itemCondition [, customerType, headers].",
            file=sys.stderr,
        )
        sys.exit(1)
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available("post_item_offers_batch.py")

    for f in ("sellerId", "region", "requests"):
        if f not in params:
            print(f"Missing required field: {f}", file=sys.stderr)
            sys.exit(1)

    raw = params["requests"]
    if not isinstance(raw, list) or not raw:
        print("requests must be a non-empty array", file=sys.stderr)
        sys.exit(1)
    if len(raw) > MAX_REQUESTS:
        print(f"At most {MAX_REQUESTS} batch sub-requests.", file=sys.stderr)
        sys.exit(1)

    use_amazon = bool(params.get("useAmazonRequestShape"))
    try:
        if use_amazon:
            requests_out = raw
        else:
            requests_out = [_expand_simple(r) for r in raw]
    except (KeyError, ValueError) as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    body_obj = {"requests": requests_out}
    seller_id = str(params["sellerId"])
    region = str(params["region"])

    tokens = get_store_tokens(seller_id, region)
    if "error" in tokens or "accessToken" not in tokens:
        print(json.dumps(tokens, indent=2, ensure_ascii=False))
        sys.exit(1)

    proxy = developer_proxy_post_json(region, PATH_BATCH, tokens["accessToken"], body_obj)
    out: dict = {
        "developerProxy": proxy,
        "resolvedPath": PATH_BATCH,
        "requestBody": body_obj,
    }
    if proxy.get("errcode") == 200 and proxy.get("httpStatus") == 200:
        br = proxy.get("body") or "{}"
        try:
            out["itemOffersBatch"] = json.loads(br)
        except json.JSONDecodeError:
            out["itemOffersBatch"] = None
            out["itemOffersBatchRaw"] = br
    emit_result(out, lf_inline_flag())


if __name__ == "__main__":
    main()
