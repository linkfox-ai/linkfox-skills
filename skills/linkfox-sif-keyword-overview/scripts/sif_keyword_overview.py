#!/usr/bin/env python3
"""
SIF Keyword Overview - LinkFox Skill
Calls the sif/keywordOverview API endpoint to retrieve keyword competition
metrics including product counts, search volume, and supply-demand ratio.

Usage:
  python sif_keyword_overview.py '{"keyword": "wireless charger", "country": "US"}'
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


API_URL = "https://tool-gateway.linkfox.com/sif/keywordOverview"


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
    """Send a POST request to the SIF keyword overview endpoint."""
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
    """Validate required parameters before making the API call."""
    if "keyword" not in params or not params["keyword"].strip():
        print("Error: 'keyword' is a required parameter and cannot be empty.", file=sys.stderr)
        sys.exit(1)

    # Validate country code if provided
    valid_countries = {
        "US", "CA", "MX", "UK", "DE", "FR", "IT", "ES",
        "JP", "IN", "AU", "BR", "NL", "SE", "PL", "TR",
        "AE", "SA", "SG",
    }
    country = params.get("country", "US")
    if country not in valid_countries:
        print(
            f"Error: Invalid country code '{country}'. "
            f"Valid codes: {', '.join(sorted(valid_countries))}",
            file=sys.stderr,
        )
        sys.exit(1)

    # Validate keyword length
    if len(params["keyword"]) > 1000:
        print("Error: 'keyword' exceeds the maximum length of 1000 characters.", file=sys.stderr)
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Usage: sif_keyword_overview.py '<JSON parameters>'", file=sys.stderr)
        print(
            'Example: sif_keyword_overview.py \'{"keyword": "wireless charger", "country": "US"}\'',
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
