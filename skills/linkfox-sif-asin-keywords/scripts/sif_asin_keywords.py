#!/usr/bin/env python3
"""
SIF ASIN Keywords Query - LinkFox Skill
Calls the sif/asinKeywords API endpoint to retrieve traffic keywords for a given ASIN.

Usage:
  python sif_asin_keywords.py '{"asin": "B0XXXXXXXX", "country": "US"}'
  python sif_asin_keywords.py '{"asin": "B0XXXXXXXX", "country": "JP", "keyword": "charger", "conditions": "nfPosition", "sortBy": "estSearchesNum", "desc": true}'
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


API_URL = "https://tool-gateway.linkfox.com/sif/asinKeywords"

# Valid marketplace codes
VALID_COUNTRIES = {
    "US", "CA", "MX", "UK", "DE", "FR", "IT", "ES",
    "JP", "IN", "AU", "BR", "NL", "SE", "PL", "TR",
    "AE", "SA", "SG",
}

# Valid condition filter values
VALID_CONDITIONS = {
    "nfPosition", "isSpAd", "isBrandAd", "isVedioAd",
    "isAC", "isER", "isTr", "isMainKw", "isAccurateKw",
    "isAccurateAboveKw", "isAccurateTailKw", "isPurchaseKw",
    "isQualityKw", "isStableKw", "isLossKw", "isInvalidKw",
}

# Valid sort field values
VALID_SORT_FIELDS = {"lastRank", "adLastRank", "updateTime", "searchesRank", "estSearchesNum", ""}


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
    # asin is required
    if "asin" not in params or not params["asin"]:
        print("Error: 'asin' is a required parameter.", file=sys.stderr)
        sys.exit(1)

    # Validate country code if provided
    country = params.get("country", "US")
    if country not in VALID_COUNTRIES:
        print(
            f"Error: Invalid country code '{country}'. "
            f"Valid values: {', '.join(sorted(VALID_COUNTRIES))}",
            file=sys.stderr,
        )
        sys.exit(1)

    # Validate conditions if provided
    if "conditions" in params and params["conditions"]:
        for cond in params["conditions"].split(","):
            cond = cond.strip()
            if cond not in VALID_CONDITIONS:
                print(
                    f"Error: Invalid condition '{cond}'. "
                    f"Valid values: {', '.join(sorted(VALID_CONDITIONS))}",
                    file=sys.stderr,
                )
                sys.exit(1)

    # Validate sortBy if provided
    if "sortBy" in params and params["sortBy"] not in VALID_SORT_FIELDS:
        print(
            f"Error: Invalid sortBy value '{params['sortBy']}'. "
            f"Valid values: {', '.join(f for f in sorted(VALID_SORT_FIELDS) if f)}",
            file=sys.stderr,
        )
        sys.exit(1)

    # Validate pageSize range if provided
    if "pageSize" in params:
        ps = params["pageSize"]
        if not isinstance(ps, int) or ps < 10 or ps > 100:
            print("Error: pageSize must be an integer between 10 and 100.", file=sys.stderr)
            sys.exit(1)


def call_api(params: dict) -> dict:
    """Call the SIF ASIN Keywords API endpoint."""
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
        print("Usage: sif_asin_keywords.py '<JSON parameters>'", file=sys.stderr)
        print(
            "Example: sif_asin_keywords.py "
            "'{\"asin\": \"B0XXXXXXXX\", \"country\": \"US\"}'",
            file=sys.stderr,
        )
        print(
            "\nRequired parameter:\n"
            "  asin      - Amazon ASIN to query\n"
            "\nOptional parameters:\n"
            "  country    - Marketplace code (default: US)\n"
            "  keyword    - Keyword filter text\n"
            "  conditions - Comma-separated condition filters\n"
            "  sortBy     - Sort field (lastRank, adLastRank, updateTime, searchesRank, estSearchesNum)\n"
            "  desc       - Descending order (default: true)\n"
            "  pageNum    - Page number (default: 1)\n"
            "  pageSize   - Results per page, 10-100 (default: 100)",
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
