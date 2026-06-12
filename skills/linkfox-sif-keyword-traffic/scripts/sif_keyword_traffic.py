#!/usr/bin/env python3
"""
SIF Keyword Summary - LinkFox Skill
Calls the sif/keywordSummary API endpoint to analyze keyword traffic sources.

Usage:
  python sif_keyword_summary.py '{"searchKeyword": "wireless charger", "country": "US"}'
  python sif_keyword_summary.py '{"searchKeyword": "wireless charger", "country": "US", "condition": "isSpAd"}'
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


API_URL = "https://tool-gateway.linkfox.com/sif/keywordSummary"

# Valid marketplace codes
VALID_COUNTRIES = {
    "US", "CA", "MX", "UK", "DE", "FR", "IT", "ES",
    "JP", "IN", "AU", "BR", "NL", "SE", "PL", "TR",
    "AE", "SA", "SG",
}

# Valid condition filter values
VALID_CONDITIONS = {
    "nfPosition", "isSpAd", "isTopAd", "isBottomAd", "isVedioAd",
    "isAC", "isER", "isTR", "isTRFOB", "isBrandAd", "isPPCAd",
    "isSearchRecommend",
}


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
    """Validate request parameters before sending to the API."""
    # searchKeyword is required
    if "searchKeyword" not in params or not params["searchKeyword"]:
        print("Error: 'searchKeyword' is required and cannot be empty.", file=sys.stderr)
        sys.exit(1)

    # Validate keyword length
    if len(params["searchKeyword"]) > 1000:
        print("Error: 'searchKeyword' exceeds maximum length of 1000 characters.", file=sys.stderr)
        sys.exit(1)

    # Validate country code if provided
    if "country" in params and params["country"] not in VALID_COUNTRIES:
        print(
            f"Error: Invalid country code '{params['country']}'. "
            f"Valid values: {', '.join(sorted(VALID_COUNTRIES))}",
            file=sys.stderr,
        )
        sys.exit(1)

    # Validate condition filter if provided
    if "condition" in params and params["condition"] not in VALID_CONDITIONS:
        print(
            f"Error: Invalid condition '{params['condition']}'. "
            f"Valid values: {', '.join(sorted(VALID_CONDITIONS))}",
            file=sys.stderr,
        )
        sys.exit(1)

    # Validate pageSize range if provided
    if "pageSize" in params:
        if not isinstance(params["pageSize"], int) or not (10 <= params["pageSize"] <= 100):
            print("Error: 'pageSize' must be an integer between 10 and 100.", file=sys.stderr)
            sys.exit(1)

    # Validate pageNum if provided
    if "pageNum" in params:
        if not isinstance(params["pageNum"], int) or params["pageNum"] < 1:
            print("Error: 'pageNum' must be a positive integer.", file=sys.stderr)
            sys.exit(1)


def call_api(params: dict) -> dict:
    """Call the tool gateway API and return the parsed response."""
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
        print("Usage: sif_keyword_summary.py '<JSON parameters>'", file=sys.stderr)
        print(
            "Example: sif_keyword_summary.py "
            '\'{"searchKeyword": "wireless charger", "country": "US"}\'',
            file=sys.stderr,
        )
        print(
            "\nRequired parameters:",
            file=sys.stderr,
        )
        print("  searchKeyword  - The keyword to analyze", file=sys.stderr)
        print(
            "\nOptional parameters:",
            file=sys.stderr,
        )
        print("  country   - Marketplace code (default: US)", file=sys.stderr)
        print("  condition - Traffic source filter (e.g., nfPosition, isSpAd)", file=sys.stderr)
        print("  pageNum   - Page number (default: 1)", file=sys.stderr)
        print("  pageSize  - Results per page, 10-100 (default: 100)", file=sys.stderr)
        print("  desc      - Sort descending (default: true)", file=sys.stderr)
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
