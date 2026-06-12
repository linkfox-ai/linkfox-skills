#!/usr/bin/env python3
"""
Ruiguan Graphic Trademark Detection - LinkFox Skill
Calls the ruiguan/trademarkGraphicDetection API endpoint

Usage:
  python ruiguan_trademark_graphic_detection.py '{"imageUrl": "https://example.com/product.jpg", "topNumber": 5, "regions": "US"}'
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


API_URL = "https://tool-gateway.linkfox.com/ruiguan/trademarkGraphicDetection"


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
    if "imageUrl" not in params:
        print("Error: 'imageUrl' is a required parameter.", file=sys.stderr)
        sys.exit(1)

    if "topNumber" not in params:
        # Apply default value if not provided
        params["topNumber"] = 5

    top_number = params["topNumber"]
    if not isinstance(top_number, int) or top_number < 1 or top_number > 100:
        print("Error: 'topNumber' must be an integer between 1 and 100.", file=sys.stderr)
        sys.exit(1)


def call_api(params: dict) -> dict:
    """Call the tool gateway API."""
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
        print("Usage: ruiguan_trademark_graphic_detection.py '<JSON parameters>'", file=sys.stderr)
        print(
            "Example: ruiguan_trademark_graphic_detection.py "
            "'{\"imageUrl\": \"https://example.com/product.jpg\", \"topNumber\": 5, \"regions\": \"US\"}'",
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
