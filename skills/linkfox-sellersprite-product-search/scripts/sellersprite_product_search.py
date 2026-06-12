#!/usr/bin/env python3
"""
SellerSprite Product Search - LinkFox Skill
Calls the sellersprite/productSearch API endpoint to search and filter
Amazon products by price, sales, BSR, ratings, margin, and more.

Usage:
  python sellersprite_product_search.py '{"keyword": "yoga mat", "marketplace": "US", "minUnits": 300}'
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


API_URL = "https://tool-gateway.linkfox.com/sellersprite/productSearch"


def get_api_key():
    """Retrieve the API key from the environment, with a friendly prompt if missing."""
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
    """Send a POST request to the SellerSprite product search API."""
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


def print_summary(result: dict):
    """Print a human-readable summary of the search results."""
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        if "details" in result:
            print(f"Details: {result['details']}", file=sys.stderr)
        return

    total = result.get("total", 0)
    products = result.get("products", [])
    keyword = result.get("keyword", "")
    snapshot = result.get("dataSnapshotMonth", "")

    print(f"Total results: {total}")
    if keyword:
        print(f"Keyword: {keyword}")
    if snapshot:
        print(f"Data snapshot: {snapshot}")
    print(f"Products returned: {len(products)}")
    print("-" * 100)

    # Print a compact table header
    header = f"{'ASIN':<12} {'Price':>8} {'Sales':>8} {'Revenue':>12} {'BSR':>8} {'Rating':>6} {'Reviews':>8} {'Margin':>7} {'Fulfillment':<12}"
    print(header)
    print("-" * 100)

    for p in products:
        asin = p.get("asin", "N/A")
        price = p.get("price", 0)
        units = p.get("monthlySalesUnits", 0)
        revenue = p.get("monthlySalesRevenue", 0)
        bsr = p.get("bsr", 0)
        rating = p.get("rating", 0)
        ratings = p.get("ratings", 0)
        profit = p.get("profit", 0)
        fulfillment = p.get("fulfillment", "N/A")

        row = f"{asin:<12} {price:>8.2f} {units:>8} {revenue:>12.2f} {bsr:>8} {rating:>6.1f} {ratings:>8} {profit:>6.1f}% {fulfillment:<12}"
        print(row)


def main():
    if len(sys.argv) < 2:
        print("Usage: sellersprite_product_search.py '<JSON parameters>'", file=sys.stderr)
        print(
            "Example: sellersprite_product_search.py "
            "'{\"keyword\": \"yoga mat\", \"marketplace\": \"US\", \"minUnits\": 300}'",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid parameter format: {e}", file=sys.stderr)
        sys.exit(1)

    result = call_api(params)

    # If stdout is a terminal, print a friendly summary; otherwise output raw JSON
    if sys.stdout.isatty():
        print_summary(result)
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
