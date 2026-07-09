#!/usr/bin/env python3
"""
Amazon Store — Get Definitions Product Type (SP-API Product Type Definitions v2020-09-01)
==========================================================================================

通过 LinkFox **POST /spApi/developerProxy** 转发 **GET getDefinitionsProductType**，
获取指定 Amazon product type 的 JSON Schema 定义。

官方参考: https://developer-docs.amazon.com/sp-api/reference/getdefinitionsproducttype

Usage:
  python get_definitions_product_type.py '{
    "sellerId": "A1BCDEFGHIJK2",
    "region": "NA",
    "productType": "LUGGAGE",
    "marketplaceIds": ["ATVPDKIKX0DER"]
  }'

Optional JSON:
  querySellerId → 写入 Query 的 sellerId（卖家专属 schema；可选，常与取令牌用的 sellerId 相同）
  productTypeVersion, requirements, requirementsEnforced, locale, skipDepCheck
"""

from typing import List

import json
import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote
from urllib.error import HTTPError, URLError

from _spapi_listings_common import emit_result, lf_inline_flag
from urllib.request import Request, urlopen

DEFINITIONS_API_VERSION = "2020-09-01"

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
            "reason": "check_auth_dependency.py not found next to get_definitions_product_type.py",
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


def developer_proxy_get(
    region: str,
    path: str,
    access_token: str,
    query_string: str,
) -> dict:
    params: dict = {
        "region": region,
        "path": path,
        "method": "GET",
        "amzAccessToken": access_token,
        "queryString": query_string,
    }
    return call_api(DEVELOPER_PROXY_ENDPOINT, params)


def _norm_marketplace_ids(val: object) -> List[str]:
    if isinstance(val, str):
        return [x.strip() for x in val.split(",") if x.strip()]
    if isinstance(val, list):
        return [str(x).strip() for x in val if str(x).strip()]
    raise ValueError("marketplaceIds must be a string or non-empty array")


def _path_for_product_type(product_type: str) -> str:
    enc = quote(product_type.strip(), safe="")
    return f"definitions/{DEFINITIONS_API_VERSION}/productTypes/{enc}"


def _build_query(params: dict) -> str:
    mids = _norm_marketplace_ids(params["marketplaceIds"])
    if not mids:
        raise ValueError("marketplaceIds is required")
    if len(mids) > 1:
        raise ValueError(
            "getDefinitionsProductType: marketplaceIds is limited to one id at this time (Amazon)"
        )
    parts: List[str] = [f"marketplaceIds={quote(mids[0], safe='')}"]

    qs = params.get("querySellerId")
    if qs is not None and str(qs).strip():
        parts.append(f"sellerId={quote(str(qs).strip(), safe='')}")

    ptv = params.get("productTypeVersion")
    if ptv is not None and str(ptv).strip():
        parts.append(f"productTypeVersion={quote(str(ptv).strip(), safe='')}")

    req = params.get("requirements")
    if req is not None and str(req).strip():
        parts.append(f"requirements={quote(str(req).strip(), safe='')}")

    re_ = params.get("requirementsEnforced")
    if re_ is not None and str(re_).strip():
        parts.append(f"requirementsEnforced={quote(str(re_).strip(), safe='')}")

    loc = params.get("locale")
    if loc is not None and str(loc).strip():
        parts.append(f"locale={quote(str(loc).strip(), safe='')}")

    return "&".join(parts)


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: get_definitions_product_type.py '<JSON>'\n"
            "Required: sellerId (用于 storeTokens), region, productType, marketplaceIds (exactly one id)\n"
            "Optional: querySellerId → Query sellerId; productTypeVersion; requirements; "
            "requirementsEnforced; locale\n"
            "See https://developer-docs.amazon.com/sp-api/reference/getdefinitionsproducttype",
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

    for f in ("sellerId", "region", "productType", "marketplaceIds"):
        if f not in params:
            print(f"Missing required field: {f}", file=sys.stderr)
            sys.exit(1)

    seller_id = str(params["sellerId"])
    region = str(params["region"])
    product_type = str(params["productType"]).strip()
    if not product_type:
        print("productType must be non-empty", file=sys.stderr)
        sys.exit(1)

    try:
        query_string = _build_query(params)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    path = _path_for_product_type(product_type)
    tokens = get_store_tokens(seller_id, region)
    if "error" in tokens or "accessToken" not in tokens:
        print(json.dumps(tokens, indent=2, ensure_ascii=False))
        sys.exit(1)

    proxy = developer_proxy_get(region, path, tokens["accessToken"], query_string)
    out = {
        "developerProxy": proxy,
        "resolvedPath": path,
        "queryString": query_string,
    }
    if proxy.get("errcode") == 200 and proxy.get("httpStatus") == 200:
        body_raw = proxy.get("body") or "{}"
        try:
            out["productTypeDefinitionResult"] = json.loads(body_raw)
        except json.JSONDecodeError:
            out["productTypeDefinitionResult"] = None
            out["productTypeDefinitionResultRaw"] = body_raw
    emit_result(out, lf_inline_flag())


if __name__ == "__main__":
    main()
