#!/usr/bin/env python3
"""
Shopee Store Tokens Query - LinkFox Skill
Calls /shopee/storeTokens to get tokens for a specific store authorization

Usage:
  python store_tokens.py '{"shopId": "67890"}'
  python store_tokens.py '{"merchantId": "12345"}'
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

from _lf_output import emit_result, lf_inline_flag

# 生产默认走 tool-gateway.linkfox.com；开发/测试期可 export SHOPEE_API_BASE_URL=<url> 覆盖
API_BASE_URL = (os.environ.get("LINKFOX_TOOL_GATEWAY") or os.environ.get("SHOPEE_API_BASE_URL") or "https://tool-gateway.linkfox.com").rstrip("/")
API_ENDPOINT = f"{API_BASE_URL}/shopee/storeTokens"


def get_api_key():
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
        with urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        return {"error": f"HTTP {e.code}: {e.reason}", "details": body}
    except URLError as e:
        return {"error": f"Connection failed: {e.reason}"}


def main():
    if len(sys.argv) < 2:
        print("Usage: store_tokens.py '<JSON parameters>'", file=sys.stderr)
        print("Required: shopId OR merchantId", file=sys.stderr)
        sys.exit(1)

    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid parameter format: {e}", file=sys.stderr)
        sys.exit(1)

    if "shopId" not in params and "merchantId" not in params:
        print("Error: 'shopId' or 'merchantId' is required (choose one)", file=sys.stderr)
        sys.exit(1)

    result = call_api(params)

    def _mask_token(t):
        if not isinstance(t, str) or len(t) < 20:
            return "***"
        return t[:8] + "..." + t[-4:]

    if "accessToken" in result:
        result["accessToken"] = _mask_token(result["accessToken"])
    if "refreshToken" in result:
        result["refreshToken"] = _mask_token(result["refreshToken"])

    emit_result(result, lf_inline_flag())

    if "expireIn" in result:
        print(f"\n✓ Tokens retrieved successfully", file=sys.stderr)
        print(f"Token expires in: {result.get('expireIn')} seconds", file=sys.stderr)
        print("Note: Tokens have been masked for security.", file=sys.stderr)


if __name__ == "__main__":
    main()
