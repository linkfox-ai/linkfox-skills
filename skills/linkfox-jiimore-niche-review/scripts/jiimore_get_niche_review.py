#!/usr/bin/env python3
"""
Jiimore Niche Review from Keyword - LinkFox Skill
Calls the jiimore/getNicheReviewFromKeyword API endpoint to retrieve
niche market review analysis data for a given keyword.

Usage:
  python jiimore_get_niche_review.py '{"keyword": "yoga mat", "countryCode": "US"}'
  python jiimore_get_niche_review.py '{"keyword": "wireless earbuds", "countryCode": "US", "searchVolumeT7Min": 5000}'
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


API_URL = "https://tool-gateway.linkfox.com/jiimore/getNicheReviewFromKeyword"

# Valid values for sortField parameter
VALID_SORT_FIELDS = {
    "clickConversionRateT7", "demand", "avgPrice", "maximumPrice",
    "minimumPrice", "productCount", "searchConversionRateT7",
    "searchVolumeT7", "unitsSoldT7", "searchVolumeGrowthT7",
    "clickCountT90", "clickCountT7", "brandCount",
    "top5BrandsClickShare", "newProductsLaunchedT180",
    "successfulLaunchesT180", "launchRateT180",
    "top5ProductsClickShare", "returnRateT360",
    "clickConversionRateT90", "searchConversionRateT90",
    "searchVolumeT90", "unitsSoldT90", "unitsSoldGrowthT90",
    "searchVolumeGrowthT90", "acos", "profitRate50",
}

# Valid country codes
VALID_COUNTRY_CODES = {"US", "JP", "DE"}


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
    # keyword is required
    if "keyword" not in params or not params["keyword"]:
        print("Error: 'keyword' is a required parameter.", file=sys.stderr)
        sys.exit(1)

    # Validate keyword length
    if len(params["keyword"]) > 1000:
        print("Error: 'keyword' must be 1000 characters or fewer.", file=sys.stderr)
        sys.exit(1)

    # Validate countryCode if provided
    if "countryCode" in params and params["countryCode"] not in VALID_COUNTRY_CODES:
        print(
            f"Error: 'countryCode' must be one of: {', '.join(sorted(VALID_COUNTRY_CODES))}",
            file=sys.stderr,
        )
        sys.exit(1)

    # Validate sortField if provided
    if "sortField" in params and params["sortField"] not in VALID_SORT_FIELDS:
        print(
            f"Error: 'sortField' must be one of: {', '.join(sorted(VALID_SORT_FIELDS))}",
            file=sys.stderr,
        )
        sys.exit(1)

    # Validate sortType if provided
    if "sortType" in params and params["sortType"] not in ("desc", "asc"):
        print("Error: 'sortType' must be 'desc' or 'asc'.", file=sys.stderr)
        sys.exit(1)

    # Validate pageSize if provided
    if "pageSize" in params:
        if not isinstance(params["pageSize"], int) or not (10 <= params["pageSize"] <= 100):
            print("Error: 'pageSize' must be an integer between 10 and 100.", file=sys.stderr)
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
        print("Usage: jiimore_get_niche_review.py '<JSON parameters>'", file=sys.stderr)
        print(
            "Example: jiimore_get_niche_review.py "
            "'{\"keyword\": \"yoga mat\", \"countryCode\": \"US\"}'",
            file=sys.stderr,
        )
        print(
            "\nRequired parameters:\n"
            "  keyword       Search keyword (use target marketplace language)\n"
            "\nOptional parameters:\n"
            "  countryCode   US (default), JP, or DE\n"
            "  page          Page number, starting from 1 (default: 1)\n"
            "  pageSize      Results per page, 10-100 (default: 50)\n"
            "  sortField     Sort field (default: unitsSoldT7)\n"
            "  sortType      desc (default) or asc\n"
            "  ...           See references/api.md for all filter parameters",
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
