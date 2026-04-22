#!/usr/bin/env python3
"""
Jungle Scout — 产品数据库查询 - LinkFox Skill
Calls the tool-jungle-scout/product-database/query API endpoint

Usage:
  python junglescout_product_database.py '{"marketplace": "us", "includeKeywords": "yoga mat", "minSales": 300, "sort": "-sales", "needCount": 20}'
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


API_URL = "https://tool-gateway.linkfox.com/tool-jungle-scout/product-database/query"

VALID_MARKETPLACES = {"us", "uk", "de", "in", "ca", "fr", "it", "es", "mx", "jp"}


def get_api_key():
    """Retrieve the API key from environment, with a friendly prompt if missing."""
    key = os.environ.get("LINKFOXAGENT_API_KEY")
    if not key:
        print(
            "API Key not configured. Please complete authorization first:\n"
            "1. Visit https://yxgb3sicy7.feishu.cn/wiki/GIkkweGghiyzkqkRXQKc2n0Tnre to obtain your Key\n"
            "2. Set the environment variable: export LINKFOXAGENT_API_KEY=your-key-here",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


def call_api(params: dict) -> dict:
    """Call the tool gateway API."""
    api_key = get_api_key()
    data = json.dumps(params).encode("utf-8")

    req = Request(
        API_URL,
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


def main():
    if len(sys.argv) < 2:
        print("Usage: junglescout_product_database.py '<JSON parameters>'", file=sys.stderr)
        print(
            'Example: junglescout_product_database.py \'{"marketplace": "us", "includeKeywords": "yoga mat", '
            '"minSales": 300, "sort": "-sales", "needCount": 20}\'',
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid parameter format: {e}", file=sys.stderr)
        sys.exit(1)

    if "marketplace" not in params:
        print("Error: missing required parameter: marketplace", file=sys.stderr)
        sys.exit(1)

    if params["marketplace"] not in VALID_MARKETPLACES:
        print(
            f"Error: invalid marketplace '{params['marketplace']}'. "
            f"Valid values: {', '.join(sorted(VALID_MARKETPLACES))}",
            file=sys.stderr,
        )
        sys.exit(1)

    result = call_api(params)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
