#!/usr/bin/env python3
"""
Amazon Store — Put Listings Item (SP-API Listings Items v2021-08-01)
===================================================================

通过 LinkFox **POST /spApi/developerProxy** 转发 **PUT putListingsItem**，
创建新刊登或对现有刊登做**全量**更新；与 get/patch 相同：先 **storeTokens**，再带 **body**（JSON 字符串）调用代理。

官方参考: https://developer-docs.amazon.com/sp-api/reference/putlistingsitem

Usage:
  python put_listings_item.py '{
    "sellerId": "A1BCDEFGHIJK2",
    "region": "NA",
    "sku": "My-Seller-SKU-001",
    "marketplaceIds": ["ATVPDKIKX0DER"],
    "productType": "LUGGAGE",
    "requirements": "LISTING",
    "attributes": { "item_name": [ { "value": "Title", "marketplace_id": "ATVPDKIKX0DER" } ] }
  }'

说明：`attributes` 须符合该 productType 的 JSON Schema；上例仅演示结构。

Optional JSON:
  includedData, mode (VALIDATION_PREVIEW), issueLocale, skipDepCheck
"""

from typing import Any, Dict, List

import json
import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote
from urllib.error import HTTPError, URLError

from _spapi_listings_common import emit_result, lf_inline_flag
from urllib.request import Request, urlopen

LISTINGS_API_VERSION = "2021-08-01"
REQUIREMENTS_SET = frozenset({"LISTING", "LISTING_PRODUCT_ONLY", "LISTING_OFFER_ONLY"})

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
            "reason": "check_auth_dependency.py not found next to put_listings_item.py",
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
        with urlopen(req, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        return {"error": f"HTTP {e.code}: {e.reason}", "details": body}
    except URLError as e:
        return {"error": f"Connection failed: {e.reason}"}


def get_store_tokens(seller_id: str, region: str) -> dict:
    return call_api(STORE_TOKENS_ENDPOINT, {"sellerId": seller_id, "region": region})


def developer_proxy_put(
    region: str,
    path: str,
    access_token: str,
    query_string: str,
    body_obj: Dict[str, Any],
) -> dict:
    params: dict = {
        "region": region,
        "path": path,
        "method": "PUT",
        "amzAccessToken": access_token,
        "queryString": query_string,
        "body": json.dumps(body_obj, ensure_ascii=False),
        "contentType": "application/json",
    }
    return call_api(DEVELOPER_PROXY_ENDPOINT, params)


def _path_put(seller_id: str, sku: str) -> str:
    return (
        f"listings/{LISTINGS_API_VERSION}/items/"
        f"{quote(seller_id, safe='')}/{quote(sku, safe='')}"
    )


def _norm_marketplace_ids(val: object) -> List[str]:
    if isinstance(val, str):
        return [x.strip() for x in val.split(",") if x.strip()]
    if isinstance(val, list):
        return [str(x).strip() for x in val if str(x).strip()]
    raise ValueError("marketplaceIds must be a string or non-empty array")


def _build_put_query(params: dict) -> str:
    mids = _norm_marketplace_ids(params["marketplaceIds"])
    if not mids:
        raise ValueError("marketplaceIds is required")
    if len(mids) > 1:
        raise ValueError(
            "putListingsItem requires at most one marketplace id (Amazon: marketplaceIds length ≤ 1)"
        )
    parts: List[str] = [f"marketplaceIds={quote(mids[0], safe='')}"]

    inc = params.get("includedData")
    if inc is not None:
        if isinstance(inc, list):
            iv = ",".join(str(x) for x in inc)
        else:
            iv = str(inc).strip()
        if iv:
            parts.append(f"includedData={quote(iv, safe='')}")

    mode = params.get("mode")
    if mode is not None and str(mode).strip():
        parts.append(f"mode={quote(str(mode).strip(), safe='')}")

    il = params.get("issueLocale")
    if il is not None and str(il).strip():
        parts.append(f"issueLocale={quote(str(il).strip(), safe='')}")

    return "&".join(parts)


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: put_listings_item.py '<JSON>'\n"
            "Required: sellerId, region, sku, marketplaceIds (exactly one id), "
            "productType, requirements, attributes (object)\n"
            "requirements: LISTING | LISTING_PRODUCT_ONLY | LISTING_OFFER_ONLY\n"
            "Optional: includedData, mode (e.g. VALIDATION_PREVIEW), issueLocale\n"
            "See https://developer-docs.amazon.com/sp-api/reference/putlistingsitem",
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

    for f in ("sellerId", "region", "sku", "marketplaceIds", "productType", "requirements", "attributes"):
        if f not in params:
            print(f"Missing required field: {f}", file=sys.stderr)
            sys.exit(1)

    seller_id = str(params["sellerId"])
    region = str(params["region"])
    sku = str(params["sku"])
    product_type = str(params["productType"])
    requirements = str(params["requirements"]).strip()

    if requirements not in REQUIREMENTS_SET:
        print(
            f"requirements must be one of {sorted(REQUIREMENTS_SET)}",
            file=sys.stderr,
        )
        sys.exit(1)

    attrs = params["attributes"]
    if not isinstance(attrs, dict):
        print("attributes must be a JSON object", file=sys.stderr)
        sys.exit(1)

    try:
        query_string = _build_put_query(params)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    body_obj: Dict[str, Any] = {
        "productType": product_type,
        "requirements": requirements,
        "attributes": attrs,
    }

    path = _path_put(seller_id, sku)
    tokens = get_store_tokens(seller_id, region)
    if "error" in tokens or "accessToken" not in tokens:
        print(json.dumps(tokens, indent=2, ensure_ascii=False))
        sys.exit(1)

    access_token = tokens["accessToken"]
    proxy = developer_proxy_put(region, path, access_token, query_string, body_obj)

    out: Dict[str, Any] = {
        "developerProxy": proxy,
        "resolvedPath": path,
        "queryString": query_string,
        "requestBody": body_obj,
    }
    if proxy.get("errcode") == 200 and proxy.get("httpStatus") == 200:
        body_raw = proxy.get("body") or "{}"
        try:
            out["putResult"] = json.loads(body_raw)
        except json.JSONDecodeError:
            out["putResult"] = None
            out["putResultRaw"] = body_raw
    emit_result(out, lf_inline_flag())


if __name__ == "__main__":
    main()
