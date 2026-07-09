#!/usr/bin/env python3
"""
Amazon Store — getListingOffers (SP-API Product Pricing v0)
===========================================================

通过 LinkFox 店铺网关 **POST /spApi/developerProxy** 转发 **GET getListingOffers**，
返回**单个**卖家 SKU 在指定站点、指定成色下的最低报价类信息（以 Amazon 响应为准）。

官方参考: https://developer-docs.amazon.com/sp-api/reference/getlistingoffers

Usage:
  python get_listing_offers.py '{
    "sellerId": "A1BCDEFGHIJK2",
    "region": "NA",
    "sku": "My-Seller-SKU-001",
    "marketplaceId": "ATVPDKIKX0DER",
    "itemCondition": "New"
  }'

Optional JSON fields:
  - customerType: Consumer | Business
  - marketplaceIds: 若提供数组则仅取第一个作为 MarketplaceId
  - skipDepCheck: boolean
"""

from __future__ import annotations

from typing import Optional

import json
import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from _spapi_pricing_common import emit_result, lf_inline_flag

LISTING_OFFERS_PREFIX = "products/pricing/v0/listings"

API_BASE_URL = (
    os.environ.get("LINKFOX_TOOL_GATEWAY")
    or os.environ.get("STORE_API_BASE_URL")
    or os.environ.get("SPAPI_BASE_URL", "https://tool-gateway.linkfox.com")
)
STORE_TOKENS_ENDPOINT = f"{API_BASE_URL.rstrip('/')}/spApi/storeTokens"
DEVELOPER_PROXY_ENDPOINT = f"{API_BASE_URL.rstrip('/')}/spApi/developerProxy"

REQUIRED_SKILL = "linkfox-amazon-store-auth"
DEPENDENCY_EXIT_CODE = 42


def ensure_auth_skill_available() -> None:
    here = Path(__file__).resolve().parent
    checker = here / "check_auth_dependency.py"
    if not checker.exists():
        payload = {
            "missingSkill": REQUIRED_SKILL,
            "reason": "check_auth_dependency.py not found next to get_listing_offers.py",
        }
        print(f"DEPENDENCY_MISSING: {json.dumps(payload, ensure_ascii=False)}", file=sys.stderr)
        sys.exit(DEPENDENCY_EXIT_CODE)
    try:
        result = subprocess.run(
            [sys.executable, str(checker)],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except Exception as exc:  # pragma: no cover
        payload = {"missingSkill": REQUIRED_SKILL, "reason": str(exc)}
        print(f"DEPENDENCY_MISSING: {json.dumps(payload, ensure_ascii=False)}", file=sys.stderr)
        sys.exit(DEPENDENCY_EXIT_CODE)
    if result.stderr:
        sys.stderr.write(result.stderr)
        if not result.stderr.endswith("\n"):
            sys.stderr.write("\n")
    if result.returncode != 0:
        sys.exit(DEPENDENCY_EXIT_CODE)


def get_api_key() -> str:
    key = os.environ.get("LINKFOX_AGENT_API_KEY") or os.environ.get("LINKFOXAGENT_API_KEY")
    if not key:
        print(
            "API Key not configured. Set:\n  export LINKFOXAGENT_API_KEY=<your-key>",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


def call_api(endpoint: str, params: dict) -> dict:
    api_key = get_api_key()
    data = json.dumps(params).encode("utf-8")
    req = Request(
        endpoint,
        data=data,
        headers={
            "Authorization": api_key,
            "Content-Type": "application/json",
            "User-Agent": "LinkFox-Skill/1.0",
        },
        method="POST",
    )
    try:
        with urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        return {"error": f"HTTP {e.code}: {e.reason}", "details": body}
    except URLError as e:
        return {"error": f"Connection failed: {e.reason}"}


def get_store_tokens(seller_id: str, region: str) -> dict:
    return call_api(STORE_TOKENS_ENDPOINT, {"sellerId": seller_id, "region": region})


def developer_proxy_get(
    region: str,
    path: str,
    access_token: str,
    query_string: Optional[str] = None,
) -> dict:
    params: dict = {
        "region": region,
        "path": path,
        "method": "GET",
        "amzAccessToken": access_token,
    }
    if query_string:
        params["queryString"] = query_string
    return call_api(DEVELOPER_PROXY_ENDPOINT, params)


def _path_for_listing_offers(sku: str) -> str:
    enc_sku = quote(sku, safe="")
    return f"{LISTING_OFFERS_PREFIX}/{enc_sku}/offers"


def _build_query_string(
    marketplace_id: str,
    item_condition: str,
    customer_type: Optional[str],
) -> str:
    parts: list[str] = [
        f"MarketplaceId={quote(marketplace_id, safe='')}",
        f"ItemCondition={quote(item_condition.strip(), safe='')}",
    ]
    if customer_type:
        parts.append(f"CustomerType={quote(customer_type.strip(), safe='')}")
    return "&".join(parts)


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: get_listing_offers.py '<JSON>'\n"
            "Required: sellerId, region, sku (seller SKU), marketplaceId (or marketplaceIds[0]), "
            "itemCondition (New|Used|Collectible|Refurbished|Club).\n"
            "Example: get_listing_offers.py "
            '\'{"sellerId":"A1...","region":"NA","sku":"MY-SKU","marketplaceId":"ATVPDKIKX0DER",'
            '"itemCondition":"New"}\'',
            file=sys.stderr,
        )
        sys.exit(1)
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if not params.get("skipDepCheck"):
        ensure_auth_skill_available()

    for f in ("sellerId", "region", "sku", "itemCondition"):
        if f not in params:
            print(f"Missing required field: {f}", file=sys.stderr)
            sys.exit(1)

    mid = params.get("marketplaceId")
    if mid is None and params.get("marketplaceIds") is not None:
        mids = params["marketplaceIds"]
        if isinstance(mids, list) and mids:
            mid = mids[0]
            if len(mids) > 1:
                print(
                    "⚠️  Warning: getListingOffers expects a single MarketplaceId; "
                    "using first marketplaceIds only.",
                    file=sys.stderr,
                )
        elif isinstance(mids, str) and mids.strip():
            mid = mids.strip()
    if mid is None or (isinstance(mid, str) and not mid.strip()):
        print("Missing marketplaceId (or non-empty marketplaceIds)", file=sys.stderr)
        sys.exit(1)
    marketplace_id = str(mid).strip()

    seller_id = str(params["sellerId"])
    region = str(params["region"])
    sku = str(params["sku"])
    if not sku.strip():
        print("sku must be non-empty", file=sys.stderr)
        sys.exit(1)

    item_condition = str(params["itemCondition"])
    customer_type = params.get("customerType")
    if customer_type is not None:
        customer_type = str(customer_type)

    query_string = _build_query_string(marketplace_id, item_condition, customer_type)
    path = _path_for_listing_offers(sku)

    tokens = get_store_tokens(seller_id, region)
    if "error" in tokens or "accessToken" not in tokens:
        print(json.dumps(tokens, indent=2, ensure_ascii=False))
        sys.exit(1)

    access_token = tokens["accessToken"]
    proxy = developer_proxy_get(region, path, access_token, query_string)

    out: dict = {
        "developerProxy": proxy,
        "resolvedPath": path,
        "queryString": query_string,
    }
    if proxy.get("errcode") == 200 and proxy.get("httpStatus") == 200:
        body_raw = proxy.get("body") or "{}"
        try:
            out["listingOffers"] = json.loads(body_raw)
        except json.JSONDecodeError:
            out["listingOffers"] = None
            out["listingOffersRaw"] = body_raw
    emit_result(out, lf_inline_flag())


if __name__ == "__main__":
    main()
