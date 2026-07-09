#!/usr/bin/env python3
"""
Amazon Ads Authorized Stores List - LinkFox Skill
Calls /amazonAds/authorizedStores to list all authorized ad accounts x marketplaces

Usage:
  python authorized_stores.py
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

from _lf_output import emit_result, lf_inline_flag

# 生产默认走 tool-gateway.linkfox.com；开发/测试期可 export AMAZON_ADS_BASE_URL=<url> 覆盖
API_BASE_URL = (os.environ.get("LINKFOX_TOOL_GATEWAY") or os.environ.get("AMAZON_ADS_BASE_URL") or "https://tool-gateway.linkfox.com").rstrip("/")
API_ENDPOINT = f"{API_BASE_URL}/amazonAds/authorizedStores"


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


def call_api() -> dict:
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
        with urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        return {"error": f"HTTP {e.code}: {e.reason}", "details": body}
    except URLError as e:
        return {"error": f"Connection failed: {e.reason}"}


def main():
    result = call_api()
    emit_result(result, lf_inline_flag())

    if "stores" in result:
        stores = result.get("stores", [])
        total = result.get("total", 0)
        print(f"\n✓ Found {total} authorized ad account(s):", file=sys.stderr)
        for s in stores:
            print(
                f"  - profileId={s.get('profileId')}  {s.get('accountInfoName', 'N/A')}  "
                f"{s.get('countryCode', '')} ({s.get('region', '')})  "
                f"marketplace={s.get('marketplaceStringId', '')}",
                file=sys.stderr,
            )


if __name__ == "__main__":
    main()
