#!/usr/bin/env python3
"""
Amazon Store — getFeaturedOfferExpectedPriceBatch (Product Pricing 2022-05-01)
==============================================================================

POST FOEP 批量接口（单批最多 40 条子请求，以 Amazon 文档为准）。

官方参考: https://developer-docs.amazon.com/sp-api/reference/getfeaturedofferexpectedpricebatch

JSON 入参（简化）:
  sellerId, region,
  requests: [ { "marketplaceId", "sku", "segment" }, ... ]

segment 须符合 SP-API 模型（地理/配送等），见官方文档。

可选 useAmazonRequestShape: true — requests 为 Amazon 完整子请求对象（含 uri、method 等）。
"""

from __future__ import annotations

import json
import sys

from _spapi_pricing_common import (
    developer_proxy_post_json,
    emit_result,
    ensure_auth_skill_available,
    get_store_tokens,
    lf_inline_flag,
)

PATH_BATCH = "batches/products/pricing/2022-05-01/offer/featuredOfferExpectedPrice"
URI_SUB = "/products/pricing/2022-05-01/offer/featuredOfferExpectedPrice"
MAX_REQUESTS = 40


def _expand_simple(req: dict) -> dict:
    mid = str(req.get("marketplaceId") or "").strip()
    sku = str(req.get("sku") or "").strip()
    if not mid or not sku:
        raise ValueError("each request needs marketplaceId and sku")
    if "segment" not in req or not isinstance(req["segment"], dict):
        raise ValueError("each request needs segment (object) per Amazon schema")
    return {
        "uri": URI_SUB,
        "method": "POST",
        "marketplaceId": mid,
        "sku": sku,
        "segment": req["segment"],
    }


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: post_featured_offer_expected_price_batch.py '<JSON>'\n"
            f"Required: sellerId, region, requests (1..{MAX_REQUESTS}).\n"
            "Each item: marketplaceId, sku, segment (object).",
            file=sys.stderr,
        )
        sys.exit(1)
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available("post_featured_offer_expected_price_batch.py")

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
        requests_out = raw if use_amazon else [_expand_simple(r) for r in raw]
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
            out["featuredOfferExpectedPriceBatch"] = json.loads(br)
        except json.JSONDecodeError:
            out["featuredOfferExpectedPriceBatch"] = None
            out["featuredOfferExpectedPriceBatchRaw"] = br
    emit_result(out, lf_inline_flag())


if __name__ == "__main__":
    main()
