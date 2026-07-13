#!/usr/bin/env python3
"""
Amazon Authorized Stores List - LinkFox Skill
Calls the /spApi/authorizedStores endpoint to list all authorized stores

Usage:
  python authorized_stores.py
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
API_ENDPOINT = f"{API_BASE_URL}/spApi/authorizedStores"


def get_api_key():
    """
    获取配置在环境变量的API Key。
    如果获取不到，按 SKILL.md 的 **## 解决认证和积分问题** 处理。
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


def call_api() -> dict:
    """Call the authorized stores API."""
    api_key = get_api_key()

    req = Request(
        API_ENDPOINT,
        data=b"{}",
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
    result = call_api()
    emit_result(result, lf_inline_flag())

    # If successful, print summary
    if "stores" in result:
        stores = result.get("stores", [])
        total = result.get("total", 0)
        print(f"\n✓ Found {total} authorized store(s):", file=sys.stderr)
        for store in stores:
            print(f"  - {store.get('sellerName', 'N/A')} ({store.get('sellerId')}) - {store.get('region')}", file=sys.stderr)


if __name__ == "__main__":
    main()
