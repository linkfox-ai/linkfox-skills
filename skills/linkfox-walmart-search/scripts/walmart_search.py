#!/usr/bin/env python3
"""
Walmart Product Search - LinkFox Skill
Calls the walmart/search API endpoint to retrieve Walmart product listings.

Usage:
  python walmart_search.py '{"keyword": "wireless earbuds", "sort": "best_seller"}'
  python walmart_search.py '{"keyword": "laptop stand", "minPrice": 10, "maxPrice": 50}'
  python walmart_search.py '{"categoryId": "976759_976787", "page": 1}'
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


API_URL = "https://tool-gateway.linkfox.com/walmart/search"


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
    """Call the Walmart search API endpoint via the LinkFox tool gateway."""
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
    """Validate that at least one of keyword or categoryId is provided."""
    if not params.get("keyword") and not params.get("categoryId"):
        print(
            "Error: At least one of 'keyword' or 'categoryId' must be provided.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Validate page range if provided
    page = params.get("page")
    if page is not None and (page < 1 or page > 100):
        print(
            "Error: 'page' must be between 1 and 100.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Validate sort value if provided
    valid_sorts = {"price_low", "price_high", "best_seller", "best_match"}
    sort = params.get("sort")
    if sort is not None and sort not in valid_sorts:
        print(
            f"Error: 'sort' must be one of {valid_sorts}.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Validate device value if provided
    valid_devices = {"desktop", "tablet", "mobile"}
    device = params.get("device")
    if device is not None and device not in valid_devices:
        print(
            f"Error: 'device' must be one of {valid_devices}.",
            file=sys.stderr,
        )
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Usage: walmart_search.py '<JSON parameters>'", file=sys.stderr)
        print(
            'Example: walmart_search.py \'{"keyword": "wireless earbuds", "sort": "best_seller"}\'',
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
