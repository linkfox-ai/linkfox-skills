#!/usr/bin/env python3
"""
Amazon Store — Get Listings Restrictions (SP-API Listings Restrictions v2021-08-01)
==================================================================================

通过 LinkFox **POST /spApi/developerProxy** 转发 **GET getListingsRestrictions**，
查询目录 ASIN 在指定卖家与市场下的刊登限制。

官方参考: https://developer-docs.amazon.com/sp-api/reference/getlistingsrestrictions

Usage:
  python get_listings_restrictions.py '{
    "sellerId": "A1BCDEFGHIJK2",
    "region": "NA",
    "asin": "B08N5WRWNW",
    "marketplaceIds": ["ATVPDKIKX0DER"]
  }'

Optional JSON:
  conditionType (enum, 如 new / used_like_new 等), reasonLocale, skipDepCheck
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

LISTINGS_API_VERSION = "2021-08-01"
RESTRICTIONS_PATH = f"listings/{LISTINGS_API_VERSION}/restrictions"

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
            "reason": "check_auth_dependency.py not found next to get_listings_restrictions.py",
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


def _build_query(params: dict, seller_id: str, asin: str) -> str:
    mids = _norm_marketplace_ids(params["marketplaceIds"])
    if not mids:
        raise ValueError("marketplaceIds is required")
    parts: List[str] = [
        f"asin={quote(asin, safe='')}",
        f"sellerId={quote(seller_id, safe='')}",
        f"marketplaceIds={quote(','.join(mids), safe='')}",
    ]
    ct = params.get("conditionType")
    if ct is not None and str(ct).strip():
        parts.append(f"conditionType={quote(str(ct).strip(), safe='')}")
    rl = params.get("reasonLocale")
    if rl is not None and str(rl).strip():
        parts.append(f"reasonLocale={quote(str(rl).strip(), safe='')}")
    return "&".join(parts)


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: get_listings_restrictions.py '<JSON>'\n"
            "Required: sellerId, region, asin, marketplaceIds\n"
            "Optional: conditionType, reasonLocale\n"
            "See https://developer-docs.amazon.com/sp-api/reference/getlistingsrestrictions",
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

    for f in ("sellerId", "region", "asin", "marketplaceIds"):
        if f not in params:
            print(f"Missing required field: {f}", file=sys.stderr)
            sys.exit(1)

    seller_id = str(params["sellerId"])
    region = str(params["region"])
    asin = str(params["asin"]).strip()
    if not asin:
        print("asin must be non-empty", file=sys.stderr)
        sys.exit(1)

    try:
        query_string = _build_query(params, seller_id, asin)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    tokens = get_store_tokens(seller_id, region)
    if "error" in tokens or "accessToken" not in tokens:
        print(json.dumps(tokens, indent=2, ensure_ascii=False))
        sys.exit(1)

    proxy = developer_proxy_get(region, RESTRICTIONS_PATH, tokens["accessToken"], query_string)
    out = {
        "developerProxy": proxy,
        "resolvedPath": RESTRICTIONS_PATH,
        "queryString": query_string,
    }
    if proxy.get("errcode") == 200 and proxy.get("httpStatus") == 200:
        body_raw = proxy.get("body") or "{}"
        try:
            out["restrictionsResult"] = json.loads(body_raw)
        except json.JSONDecodeError:
            out["restrictionsResult"] = None
            out["restrictionsResultRaw"] = body_raw
    emit_result(out, lf_inline_flag())


if __name__ == "__main__":
    main()
