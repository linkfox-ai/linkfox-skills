#!/usr/bin/env python3
"""
Amazon Store Tokens Query - LinkFox Skill
Calls the /spApi/storeTokens endpoint to get store tokens

Usage:
  python store_tokens.py '{"sellerId": "A1234567890", "region": "NA"}'
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from _lf_output import emit_result, lf_inline_flag
from _token_status_output import strip_raw_tokens, print_status_note

API_BASE_URL = (
    os.environ.get("LINKFOX_TOOL_GATEWAY")
    or os.environ.get("STORE_API_BASE_URL")
    or os.environ.get("SPAPI_BASE_URL")
    or "https://tool-gateway.linkfox.com"
).rstrip("/")
API_ENDPOINT = f"{API_BASE_URL}/spApi/storeTokens"


def get_api_key():
    """
    获取配置在环境变量的API Key。
    如果获取不到，按 SKILL.md 的 **## 解决认证和算力问题** 处理。
    Retrieve the API key from environment, with a friendly prompt if missing.
    """
    key = os.environ.get("LINKFOX_AGENT_API_KEY") or os.environ.get("LINKFOXAGENT_API_KEY")
    if not key:
        print(
            "API Key 未配置",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


def call_api(params: dict) -> dict:
    """Call the store tokens API."""
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
        with urlopen(req, timeout=150) as response:
            result = json.loads(response.read().decode("utf-8"))
            error_code = str(result.get("errcode", ""))
            if error_code.isdigit() and 1500 <= int(error_code) <= 1599:
                raise SystemExit(json.dumps(result, ensure_ascii=False))
            return result
    except HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        return {"error": f"HTTP {e.code}: {e.reason}", "details": body}
    except URLError as e:
        return {"error": f"Connection failed: {e.reason}"}


def main():
    if len(sys.argv) < 2:
        print("Usage: store_tokens.py '<JSON parameters>'", file=sys.stderr)
        print(
            'Example: store_tokens.py \'{"sellerId": "A1234567890", "region": "NA"}\'',
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid parameter format: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate required fields
    if "sellerId" not in params or "region" not in params:
        print("Error: Both 'sellerId' and 'region' parameters are required", file=sys.stderr)
        sys.exit(1)

    result = call_api(params)
    result = strip_raw_tokens(result)
    emit_result(result, lf_inline_flag())
    print_status_note(result)


if __name__ == "__main__":
    main()
