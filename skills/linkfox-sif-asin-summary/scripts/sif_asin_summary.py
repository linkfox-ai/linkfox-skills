#!/usr/bin/env python3
"""
SIF ASIN Summary - LinkFox Skill
Calls the sif/asinSummary API endpoint to retrieve ASIN traffic source data.

Usage:
  python sif_asin_summary.py '{"searchValue": "B09V3KXJPB", "country": "US"}'
  python sif_asin_summary.py '{"searchValue": "B09V3KXJPB,B0BN1K7WJP", "country": "US"}'
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


API_URL = "https://tool-gateway.linkfox.com/sif/asinSummary"


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


def validate_params(params: dict):
    """Validate required parameters before making the API call."""
    if "searchValue" not in params or not params["searchValue"].strip():
        print("Error: 'searchValue' is required. Provide one or more ASINs separated by commas.", file=sys.stderr)
        sys.exit(1)

    # Check ASIN count limit
    asins = [a.strip() for a in params["searchValue"].split(",") if a.strip()]
    if len(asins) > 10:
        print(f"Error: Maximum 10 ASINs per request, but {len(asins)} were provided.", file=sys.stderr)
        sys.exit(1)

    # Validate country code if provided
    valid_countries = {"US", "CA", "MX", "UK", "DE", "FR", "IT", "ES", "JP", "IN", "AU", "BR", "NL", "SE", "PL", "TR", "AE", "SA", "SG"}
    country = params.get("country", "US")
    if country not in valid_countries:
        print(f"Error: Invalid country code '{country}'. Valid codes: {', '.join(sorted(valid_countries))}", file=sys.stderr)
        sys.exit(1)

    # Validate pageSize if provided
    page_size = params.get("pageSize", 100)
    if not (10 <= page_size <= 100):
        print(f"Error: 'pageSize' must be between 10 and 100, got {page_size}.", file=sys.stderr)
        sys.exit(1)


def call_api(params: dict) -> dict:
    """Call the SIF ASIN Summary API endpoint."""
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


def main():
    if len(sys.argv) < 2:
        print("Usage: sif_asin_summary.py '<JSON parameters>'", file=sys.stderr)
        print(
            'Example: sif_asin_summary.py \'{"searchValue": "B09V3KXJPB", "country": "US"}\'',
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
