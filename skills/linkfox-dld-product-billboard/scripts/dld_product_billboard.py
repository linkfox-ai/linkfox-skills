#!/usr/bin/env python3
"""
DLD Product Billboard - LinkFox Skill
Calls the dld/productBillboard API endpoint to query 1688 bestseller rankings.

Usage:
  python dld_product_billboard.py '<JSON parameters>'

Examples:
  # Monthly bestsellers for phone cases
  python dld_product_billboard.py '{"keyWord": "手机壳", "pageType": 3, "date": "2026-03-01"}'

  # Weekly billboard sorted by revenue
  python dld_product_billboard.py '{"keyWord": "瑜伽垫", "pageType": 2, "date": "2026-03-22", "sortField": "saleVolume"}'

  # Factory-direct products with price filter
  python dld_product_billboard.py '{"keyWord": "耳机", "companyType": 2, "beginPrice": 5, "endPrice": 30}'
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


API_URL = "https://tool-gateway.linkfox.com/dld/productBillboard"


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
    """Send a POST request to the DLD product billboard API."""
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


def format_product_summary(product: dict) -> str:
    """Format a single product record into a readable summary line."""
    title = product.get("title", "N/A")
    price = product.get("price", "N/A")
    consign_price = product.get("consignPrice", "N/A")
    orders = product.get("salesOrderCount", "N/A")
    sales_qty = product.get("salesQuantity", "N/A")
    revenue = product.get("estimatedSalesAmount", "N/A")
    company = product.get("company", "N/A")
    url = product.get("asinUrl", "")

    return (
        f"  Title: {title}\n"
        f"  Wholesale Price: {price} | Dropship Price: {consign_price}\n"
        f"  Orders: {orders} | Units Sold: {sales_qty} | Est. Revenue: {revenue}\n"
        f"  Supplier: {company}\n"
        f"  URL: {url}"
    )


def print_results(result: dict):
    """Print API results in a human-readable format."""
    # Check for errors
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        if "details" in result:
            print(f"Details: {result['details']}", file=sys.stderr)
        return

    total = result.get("total", 0)
    products = result.get("products", [])

    print(f"Total records: {total}")
    print(f"Returned: {len(products)} products")
    print("-" * 60)

    for i, product in enumerate(products, 1):
        print(f"\n[{i}]")
        print(format_product_summary(product))

    if not products:
        print("No products found. Try broadening your filters or changing the keyword.")


def main():
    if len(sys.argv) < 2:
        print("Usage: dld_product_billboard.py '<JSON parameters>'", file=sys.stderr)
        print(
            "\nExamples:",
            file=sys.stderr,
        )
        print(
            '  dld_product_billboard.py \'{"keyWord": "手机壳", "pageType": 3, "date": "2026-03-01"}\'',
            file=sys.stderr,
        )
        print(
            '  dld_product_billboard.py \'{"keyWord": "耳机", "companyType": 2, "beginPrice": 5, "endPrice": 30}\'',
            file=sys.stderr,
        )
        sys.exit(1)

    # Parse input JSON
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid parameter format: {e}", file=sys.stderr)
        sys.exit(1)

    # Call the API
    result = call_api(params)

    # Print both raw JSON and a formatted summary
    print("=== Raw JSON Response ===")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("\n=== Formatted Summary ===")
    print_results(result)


if __name__ == "__main__":
    main()
