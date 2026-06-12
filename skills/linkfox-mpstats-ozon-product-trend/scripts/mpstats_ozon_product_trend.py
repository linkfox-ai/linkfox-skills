#!/usr/bin/env python3
"""
MPSTATS Ozon Product Trend (Daily) - LinkFox Skill
Returns daily time-series for a single Ozon SKU.

Usage:
  python mpstats_ozon_product_trend.py '{"productId": 1786874757, "startDate": "2025-03-01", "endDate": "2025-03-31"}'
"""

import json
import os
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try: sys.stdout.reconfigure(encoding="utf-8")
    except Exception: pass
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


API_URL = "https://tool-gateway.linkfox.com/mpstats/ozon/productTrend"


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

    points = result.get("data", []) or []
    total = result.get("total", len(points))
    print(f"Trend points: {len(points)} | total: {total}")
    print("-" * 90)
    print(f"{'date':<12} {'price':>10} {'oldPrice':>10} {'sales':>8} {'balance':>8} {'rating':>6} {'comments':>9} {'hasData':>8}")
    print("-" * 90)
    for p in points:
        print(
            f"{(p.get('date') or ''):<12} "
            f"{(p.get('price') or 0):>10.2f} "
            f"{(p.get('oldPrice') or 0):>10.2f} "
            f"{(p.get('sales') or 0):>8} "
            f"{(p.get('balance') or 0):>8} "
            f"{(p.get('rating') or 0):>6.2f} "
            f"{(p.get('comments') or 0):>9} "
            f"{str(p.get('hasData')):>8}"
        )


def main():
    if len(sys.argv) < 2:
        print("Usage: mpstats_ozon_product_trend.py '<JSON parameters>'", file=sys.stderr)
        print(
            "Example: mpstats_ozon_product_trend.py "
            "'{\"productId\": 1786874757, \"startDate\": \"2025-03-01\", \"endDate\": \"2025-03-31\"}'",
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
