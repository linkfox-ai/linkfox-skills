#!/usr/bin/env python3
"""
Amazon Store — Get Listings Item (SP-API Listings Items v2021-08-01)
====================================================================

通过 LinkFox 店铺网关 **POST /spApi/developerProxy** 转发 **GET getListingsItem**，
与 `linkfox-amazon-store-report` 使用同一套通用代理接口。

官方参考: https://developer-docs.amazon.com/sp-api/reference/getlistingsitem

Usage:
  python get_listings_item.py '{
    "sellerId": "A1BCDEFGHIJK2",
    "region": "NA",
    "sku": "My-Seller-SKU-001",
    "marketplaceIds": ["ATVPDKIKX0DER"]
  }'

Optional JSON fields:
  - includedData: string[] 或逗号分隔字符串；默认不传则上游通常为 summaries
  - issueLocale: 例如 en_US（可选）
  - skipDepCheck: boolean，跳过依赖检查（默认 false）

Dependency:
  `linkfox-amazon-store-auth`（与 store-report 相同；启动时运行 check_auth_dependency.py）
"""

from typing import List, Optional

import json
import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from _spapi_listings_common import emit_result, lf_inline_flag

LISTINGS_API_VERSION = "2021-08-01"

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
            "reason": "check_auth_dependency.py not found next to get_listings_item.py",
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


def _path_for_get_listings_item(seller_id: str, sku: str) -> str:
    # Path segments must be percent-encoded (SKU 可含空格、斜杠等)
    enc_seller = quote(seller_id, safe="")
    enc_sku = quote(sku, safe="")
    return f"listings/{LISTINGS_API_VERSION}/items/{enc_seller}/{enc_sku}"


def _build_query_string(
    marketplace_ids: List[str],
    included_data: Optional[object],
    issue_locale: Optional[str],
) -> str:
    parts: list[str] = []
    # 官方要求 marketplaceIds；文档常见为单站点（length ≤ 1）。多传时仅取第一个并告警。
    if not marketplace_ids:
        raise ValueError("marketplaceIds must be a non-empty array of strings")
    mid = marketplace_ids[0]
    parts.append(f"marketplaceIds={quote(mid, safe='')}")
    if len(marketplace_ids) > 1:
        print(
            "⚠️  Warning: getListingsItem marketplaceIds length is typically 1; using first only.",
            file=sys.stderr,
        )
    if included_data is not None:
        if isinstance(included_data, list):
            id_val = ",".join(included_data)
        else:
            id_val = str(included_data).strip()
        if id_val:
            parts.append(f"includedData={quote(id_val, safe='')}")
    if issue_locale:
        parts.append(f"issueLocale={quote(issue_locale, safe='')}")
    return "&".join(parts)


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: get_listings_item.py '<JSON>'\n"
            "Required: sellerId, region, sku, marketplaceIds (array with ≥1 id)\n"
            "Example: get_listings_item.py "
            '\'{"sellerId":"A1...","region":"NA","sku":"ABC-1","marketplaceIds":["ATVPDKIKX0DER"]}\'',
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

    for f in ("sellerId", "region", "sku", "marketplaceIds"):
        if f not in params:
            print(f"Missing required field: {f}", file=sys.stderr)
            sys.exit(1)

    seller_id = str(params["sellerId"])
    region = str(params["region"])
    sku = str(params["sku"])
    mids = params["marketplaceIds"]
    if isinstance(mids, str):
        marketplace_ids = [mids]
    elif isinstance(mids, list):
        marketplace_ids = [str(x) for x in mids]
    else:
        print("marketplaceIds must be a string or array of strings", file=sys.stderr)
        sys.exit(1)

    included = params.get("includedData")
    issue_locale = params.get("issueLocale")
    if issue_locale is not None:
        issue_locale = str(issue_locale)

    try:
        query_string = _build_query_string(marketplace_ids, included, issue_locale)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    path = _path_for_get_listings_item(seller_id, sku)

    tokens = get_store_tokens(seller_id, region)
    if "error" in tokens or "accessToken" not in tokens:
        print(json.dumps(tokens, indent=2, ensure_ascii=False))
        sys.exit(1)

    access_token = tokens["accessToken"]
    proxy = developer_proxy_get(region, path, access_token, query_string)

    out = {
        "developerProxy": proxy,
        "resolvedPath": path,
        "queryString": query_string,
    }
    if proxy.get("errcode") == 200 and proxy.get("httpStatus") == 200:
        body_raw = proxy.get("body") or "{}"
        try:
            out["listing"] = json.loads(body_raw)
        except json.JSONDecodeError:
            out["listing"] = None
            out["listingRaw"] = body_raw
    emit_result(out, lf_inline_flag())


if __name__ == "__main__":
    main()
