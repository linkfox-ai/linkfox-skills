#!/usr/bin/env python3
"""
Ruiguan Image Compliance Search - LinkFox Skill
Calls the ruiguan image compliance API endpoint to detect
policy-violating products by product image similarity.

Usage:
  python ruiguan_image_compliance_search.py '{"imageUrl": "https://example.com/product-image.jpg"}'
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


API_URL = "https://tool-gateway.linkfox.com/ruiguan/gunPartsSearch"


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
    """Call the Ruiguan image compliance search API."""
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
            "Usage: ruiguan_image_compliance_search.py '<JSON parameters>'",
            file=sys.stderr,
        )
        print(
            'Example: ruiguan_image_compliance_search.py \'{"imageUrl": "https://example.com/product-image.jpg"}\'',
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid parameter format: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate that imageUrl is provided
    if "imageUrl" not in params or not params["imageUrl"]:
        print("Error: 'imageUrl' is required.", file=sys.stderr)
        sys.exit(1)

    # Validate URL length
    if len(params["imageUrl"]) > 1000:
        print(
            "Error: 'imageUrl' exceeds the maximum length of 1000 characters.",
            file=sys.stderr,
        )
        sys.exit(1)

    result = call_api(params)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
