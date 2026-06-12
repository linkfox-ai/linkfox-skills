#!/usr/bin/env python3
"""
MPSTATS Ozon Category Products - LinkFox Skill
Drills into all Ozon SKUs under a given Russian category full path.

Usage:
  python mpstats_ozon_category_products.py '{"categoryPath": "Одежда/Женская одежда/Футболки и топы женские", "sortField": "revenue"}'
"""

import json
import os
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try: sys.stdout.reconfigure(encoding="utf-8")
    except Exception: pass
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


API_URL = "https://tool-gateway.linkfox.com/mpstats/ozon/categoryProducts"


def get_api_key():
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
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        if "details" in result:
            print(f"Details: {result['details']}", file=sys.stderr)
        return
    total = result.get("total", 0)
    products = result.get("products", [])
    print(f"Total: {total} | Returned: {len(products)}")
    print("-" * 120)
    print(f"{'productId':<14} {'brand':<18} {'price':>10} {'sales':>8} {'revenue':>12} {'rating':>6} {'pos':>6} title")
    print("-" * 120)
    for p in products:
        pid = p.get("productId", "")
        brand = (p.get("brand") or "")[:16]
        price = p.get("price", 0) or 0
        units = p.get("monthlySalesUnits", 0) or 0
        rev = p.get("monthlySalesRevenue", 0) or 0
        rating = p.get("rating", 0) or 0
        pos = p.get("position", 0) or 0
        title = (p.get("title") or "")[:32]
        print(f"{pid!s:<14} {brand:<18} {price:>10.2f} {units:>8} {rev:>12.2f} {rating:>6.2f} {pos:>6} {title}")


def main():
    if len(sys.argv) < 2:
        print("Usage: mpstats_ozon_category_products.py '<JSON parameters>'", file=sys.stderr)
        print(
            "Example: mpstats_ozon_category_products.py "
            "'{\"categoryPath\": \"Одежда/Женская одежда/Футболки и топы женские\"}'",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid parameter format: {e}", file=sys.stderr)
        sys.exit(1)

    result = call_api(params)
    if sys.stdout.isatty():
        print_summary(result)
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
