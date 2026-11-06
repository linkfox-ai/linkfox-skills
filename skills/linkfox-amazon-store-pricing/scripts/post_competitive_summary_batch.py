#!/usr/bin/env python3
"""
Amazon Store — getCompetitiveSummary (Product Pricing 2022-05-01)
=================================================================

POST competitiveSummary 批量接口（每批 1～20 条子请求）。

官方参考: https://developer-docs.amazon.com/sp-api/reference/getcompetitivesummary

JSON 入参（简化）:
  sellerId, region,
  requests: [
    {
      "asin", "marketplaceId",
      "includedData": ["featuredBuyingOptions", ...],
      "lowestPricedOffersInputs": [...]   // 可选，仅当 includedData 含 lowestPricedOffers 时需要
    }, ...
  ]

可选 useAmazonRequestShape: true — requests 为 Amazon 完整子请求（须含 uri、method 等）。
"""

from __future__ import annotations

import json
import sys

from _spapi_pricing_common import (
    run_proxy,
    ensure_auth_skill_available,
)

PATH_BATCH = "batches/products/pricing/2022-05-01/items/competitiveSummary"
URI_SUB = "/products/pricing/2022-05-01/items/competitiveSummary"
MAX_REQUESTS = 20


def _expand_simple(req: dict) -> dict:
    asin = str(req.get("asin") or "").strip()
    mid = str(req.get("marketplaceId") or "").strip()
    if not asin or not mid:
        raise ValueError("each request needs asin and marketplaceId")
    inc = req.get("includedData")
    if not isinstance(inc, list) or not inc:
        raise ValueError("each request needs includedData (non-empty array of strings)")
    out: dict = {
        "uri": URI_SUB,
        "method": "POST",
        "asin": asin,
        "marketplaceId": mid,
        "includedData": inc,
    }
    if "lowestPricedOffersInputs" in req:
        out["lowestPricedOffersInputs"] = req["lowestPricedOffersInputs"]
    return out


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: post_competitive_summary_batch.py '<JSON>'\n"
            f"Required: sellerId, region, requests (1..{MAX_REQUESTS}).\n"
            "Each item: asin, marketplaceId, includedData [, lowestPricedOffersInputs].",
            file=sys.stderr,
        )
        sys.exit(1)
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available("post_competitive_summary_batch.py")

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

    run_proxy("getCompetitiveSummary", "POST", region, PATH_BATCH, seller_id,
              result_field="competitiveSummary", body_obj=body_obj)


if __name__ == "__main__":
    main()
