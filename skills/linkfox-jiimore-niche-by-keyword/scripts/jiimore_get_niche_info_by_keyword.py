#!/usr/bin/env python3
"""
Jiimore Niche Info by Keyword - LinkFox Skill
Calls the jiimore/getNicheInfoByKeyword API endpoint to retrieve
Amazon niche market segment data for a given keyword.

Usage:
  python jiimore_get_niche_info_by_keyword.py '{"keyword": "wireless earbuds", "countryCode": "US"}'
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


API_URL = "https://tool-gateway.linkfox.com/jiimore/getNicheInfoByKeyword"


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
    """Send a POST request to the niche info API and return the parsed response."""
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
            "Usage: jiimore_get_niche_info_by_keyword.py '<JSON parameters>'",
            file=sys.stderr,
        )
        print(
            'Example: jiimore_get_niche_info_by_keyword.py \'{"keyword": "wireless earbuds", "countryCode": "US"}\'',
            file=sys.stderr,
        )
        sys.exit(1)

    # Parse the JSON parameter string from command line
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid parameter format: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate that the required 'keyword' parameter is present
    if "keyword" not in params or not params["keyword"]:
        print("Error: 'keyword' is a required parameter.", file=sys.stderr)
        sys.exit(1)

    result = call_api(params)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
