#!/usr/bin/env python3
"""
SP-API Authorized Stores List - LinkFox Skill
Calls the /spApi/authorizedStores endpoint to list all authorized stores

Usage:
  python authorized_stores.py
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


API_BASE_URL = os.environ.get("SPAPI_BASE_URL", "https://tool-gateway.linkfox.com")
API_ENDPOINT = f"{API_BASE_URL}/spApi/authorizedStores"


def get_api_key():
    """Retrieve the API key from environment, with a friendly prompt if missing."""
    key = os.environ.get("LINKFOXAGENT_API_KEY")
    if not key:
        print(
            "API Key not configured. Please set the environment variable:\n"
            "  export LINKFOXAGENT_API_KEY=your-key-here",
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
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # If successful, print summary
    if "stores" in result:
        stores = result.get("stores", [])
        total = result.get("total", 0)
        print(f"\n✓ Found {total} authorized store(s):", file=sys.stderr)
        for store in stores:
            print(f"  - {store.get('sellerName', 'N/A')} ({store.get('sellerId')}) - {store.get('region')}", file=sys.stderr)


if __name__ == "__main__":
    main()
