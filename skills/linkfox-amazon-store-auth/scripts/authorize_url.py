#!/usr/bin/env python3
"""
Amazon Store Authorization URL - LinkFox Skill
Calls the /spApi/authorizeUrl endpoint to generate authorization URL

Usage:
  python authorize_url.py '{"region": "NA", "sellerName": "My Store"}'
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from _lf_output import emit_result, lf_inline_flag

API_BASE_URL = (
    os.environ.get("LINKFOX_TOOL_GATEWAY")
    or os.environ.get("STORE_API_BASE_URL")
    or os.environ.get("SPAPI_BASE_URL")
    or "https://tool-gateway.linkfox.com"
).rstrip("/")
API_ENDPOINT = f"{API_BASE_URL}/spApi/authorizeUrl"


def get_api_key():
    """Retrieve the API key from environment, with a friendly prompt if missing."""
    key = os.environ.get("LINKFOX_AGENT_API_KEY") or os.environ.get("LINKFOXAGENT_API_KEY")
    if not key:
        print(
            "API Key not configured. Please set the environment variable:\n"
            "  export LINKFOXAGENT_API_KEY=your-key-here",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


def call_api(params: dict) -> dict:
    """Call the authorization URL API."""
    api_key = get_api_key()
    data = json.dumps(params).encode("utf-8")

    req = Request(
        API_ENDPOINT,
        data=data,
        headers={
            "Authorization": api_key,
            "Content-Type": "application/json",
            "User-Agent": "LinkFox-Skill/1.0",
        },
        method="POST",
    )

    try:
        with urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        return {"error": f"HTTP {e.code}: {e.reason}", "details": body}
    except URLError as e:
        return {"error": f"Connection failed: {e.reason}"}


def main():
    if len(sys.argv) < 2:
        print("Usage: authorize_url.py '<JSON parameters>'", file=sys.stderr)
        print(
            'Example: authorize_url.py \'{"region": "NA", "sellerName": "My Store"}\'',
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid parameter format: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate required fields
    if "region" not in params:
        print("Error: 'region' parameter is required (NA/EU/FE)", file=sys.stderr)
        sys.exit(1)

    if "sellerName" not in params:
        print(
            "Error: 'sellerName' (店铺名) is required — 授权前必须填写可识别的店铺名称，"
            "用于在已授权店铺列表中区分账号，请勿留空或省略。",
            file=sys.stderr,
        )
        sys.exit(1)
    seller_name = params["sellerName"]
    if not isinstance(seller_name, str) or not seller_name.strip():
        print(
            "Error: 'sellerName' (店铺名) must be a non-empty string — "
            "请提供有意义的店铺名称（不能与空白相同）。",
            file=sys.stderr,
        )
        sys.exit(1)
    params["sellerName"] = seller_name.strip()

    result = call_api(params)
    emit_result(result, lf_inline_flag())

    # If successful, print helpful instructions
    if "authorizeUrl" in result:
        print("\n✓ Authorization URL generated successfully!", file=sys.stderr)
        print(
            f"店铺名已记录为: {params['sellerName']}（请确认与亚马逊后台展示名称一致，便于后续识别）。",
            file=sys.stderr,
        )
        print("Please open the following URL in your browser to authorize:", file=sys.stderr)
        print(f"\n  {result['authorizeUrl']}\n", file=sys.stderr)


if __name__ == "__main__":
    main()
