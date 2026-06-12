#!/usr/bin/env python3
"""
Jiimore Niche Market Info - LinkFox Skill
Calls the jiimore/getNicheInfo API endpoint to retrieve niche market insights.

Usage:
  python jiimore_get_niche_info.py '{"nicheId": "12345678", "countryCode": "US"}'
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


API_URL = "https://tool-gateway.linkfox.com/jiimore/getNicheInfo"


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
    if "nicheId" not in params or not params["nicheId"]:
        print("Error: 'nicheId' is required.", file=sys.stderr)
        sys.exit(1)

    # Validate countryCode if provided
    country_code = params.get("countryCode", "US")
    if country_code not in ("US", "JP", "DE"):
        print(
            f"Error: 'countryCode' must be one of US, JP, DE. Got: {country_code}",
            file=sys.stderr,
        )
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
        print("Usage: jiimore_get_niche_info.py '<JSON parameters>'", file=sys.stderr)
        print(
            'Example: jiimore_get_niche_info.py \'{"nicheId": "12345678", "countryCode": "US"}\'',
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
