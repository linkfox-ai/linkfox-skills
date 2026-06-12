#!/usr/bin/env python3
"""
WallySmarter Product Detail - LinkFox Skill
Calls the wallysmarter/productDetail API endpoint to retrieve Walmart product details
including pricing history and sales trends.

Usage:
  python wallysmarter_product_detail.py '{"productId": 5177343351}'
  python wallysmarter_product_detail.py '{"productId": 5169493923, "includeStats": false}'
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


API_URL = "https://tool-gateway.linkfox.com/wallysmarter/productDetail"


def get_api_key():
    """Retrieve the API key from environment, with a friendly prompt if missing."""
    key = os.environ.get("LINKFOXAGENT_API_KEY")
    if not key:
        print(
            "API Key not configured. Please complete authorization first:\n"
            "1. Visit https://skill.linkfox.com/linkfoxskills/guide.htm to obtain your Key\n"
            "2. Set the environment variable: export LINKFOXAGENT_API_KEY=your-key-here",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


def call_api(params: dict) -> dict:
    """Call the WallySmarter product detail API endpoint via the LinkFox tool gateway."""
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
        with urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        return {"error": f"HTTP {e.code}: {e.reason}", "details": body}
    except URLError as e:
        return {"error": f"Connection failed: {e.reason}"}


def validate_params(params: dict):
    """Validate that productId is provided."""
    if not params.get("productId"):
        print(
            "Error: 'productId' is required. Provide the Walmart Item ID "
            "(numeric ID from the product URL, e.g., 5177343351).",
            file=sys.stderr,
        )
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Usage: wallysmarter_product_detail.py '<JSON parameters>'", file=sys.stderr)
        print(
            'Example: wallysmarter_product_detail.py \'{"productId": 5177343351}\'',
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid parameter format: {e}", file=sys.stderr)
        sys.exit(1)

    validate_params(params)

    result = call_api(params)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
