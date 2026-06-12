#!/usr/bin/env python3
"""
Ruiguan Text Trademark Detection - LinkFox Skill
Calls the ruiguan/textTrademarkDetection API endpoint to scan product text
for potential trademark infringements.

Usage:
  python ruiguan_text_trademark_detection.py '{"productTitle": "Wireless Bluetooth Headphones", "regions": "US", "limit": 100}'
  python ruiguan_text_trademark_detection.py '{"productTitle": "Portable Charger", "productText": "Fast charging power bank", "regions": "US,EM", "limit": 200}'
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


API_URL = "https://tool-gateway.linkfox.com/ruiguan/textTrademarkDetection"


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
    """Validate required parameters before sending the request."""
    if "productTitle" not in params or not params["productTitle"]:
        print("Error: 'productTitle' is required and cannot be empty.", file=sys.stderr)
        sys.exit(1)

    if len(params["productTitle"]) > 1000:
        print("Error: 'productTitle' exceeds the 1000 character limit.", file=sys.stderr)
        sys.exit(1)

    if "productText" in params and len(params.get("productText", "")) > 1000:
        print("Error: 'productText' exceeds the 1000 character limit.", file=sys.stderr)
        sys.exit(1)

    # Set default limit if not provided
    if "limit" not in params:
        params["limit"] = 100

    limit = params["limit"]
    if not isinstance(limit, int) or limit < 1 or limit > 500:
        print("Error: 'limit' must be an integer between 1 and 500.", file=sys.stderr)
        sys.exit(1)

    # Validate region codes if provided
    valid_regions = {"US", "EM", "GB", "DE", "FR", "IT", "ES", "AU", "CA", "MX", "JP", "CN", "WO", "TR", "BX"}
    if "regions" in params and params["regions"]:
        user_regions = [r.strip() for r in params["regions"].split(",")]
        invalid = [r for r in user_regions if r not in valid_regions]
        if invalid:
            print(
                f"Warning: unrecognized region code(s): {', '.join(invalid)}. "
                f"Supported: {', '.join(sorted(valid_regions))}",
                file=sys.stderr,
            )


def call_api(params: dict) -> dict:
    """Call the tool gateway API and return the parsed JSON response."""
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
        with urlopen(req, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        return {"error": f"HTTP {e.code}: {e.reason}", "details": body}
    except URLError as e:
        return {"error": f"Connection failed: {e.reason}"}


def main():
    if len(sys.argv) < 2:
        print("Usage: ruiguan_text_trademark_detection.py '<JSON parameters>'", file=sys.stderr)
        print(
            "Example: ruiguan_text_trademark_detection.py "
            "'{\"productTitle\": \"Wireless Bluetooth Headphones\", \"regions\": \"US\", \"limit\": 100}'",
            file=sys.stderr,
        )
        sys.exit(1)

    # Parse the JSON parameter string from command line
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid parameter format: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate parameters before calling the API
    validate_params(params)

    # Call the API and print the result
    result = call_api(params)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
