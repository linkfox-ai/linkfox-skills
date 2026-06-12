#!/usr/bin/env python3
"""
Jiimore Niche Competitor by ASIN - LinkFox Skill
Calls the jiimore/pageAsinsByAsin API endpoint to retrieve
competing products within the same niche for a given reference ASIN.

Usage:
  python jiimore_page_asins_by_asin.py '{"asin": "B0GC4RPX79", "countryCode": "US"}'
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


API_URL = "https://tool-gateway.linkfox.com/jiimore/pageAsinsByAsin"


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
    """Send a POST request to the niche competitor API and return the parsed response."""
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
        print(
            "Usage: jiimore_page_asins_by_asin.py '<JSON parameters>'",
            file=sys.stderr,
        )
        print(
            'Example: jiimore_page_asins_by_asin.py \'{"asin": "B0GC4RPX79", "countryCode": "US"}\'',
            file=sys.stderr,
        )
        sys.exit(1)

    # Parse the JSON parameter string from command line
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid parameter format: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate that the required 'asin' parameter is present
    if "asin" not in params or not params["asin"]:
        print("Error: 'asin' is a required parameter.", file=sys.stderr)
        sys.exit(1)

    result = call_api(params)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
