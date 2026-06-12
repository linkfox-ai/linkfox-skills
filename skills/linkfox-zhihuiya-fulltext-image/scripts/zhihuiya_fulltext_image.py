#!/usr/bin/env python3
"""
Zhihuiya Patent Fulltext Image Query - LinkFox Skill
Calls the zhihuiya/fulltextImage API endpoint to retrieve patent drawings and figures.

Usage:
  python zhihuiya_fulltext_image.py '{"patentNumber": "US20230012345A1", "limit": "100", "offset": "0"}'
  python zhihuiya_fulltext_image.py '{"patentId": "abc123def456"}'
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


API_URL = "https://tool-gateway.linkfox.com/zhihuiya/fulltextImage"


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
    """Ensure at least one patent identifier is provided."""
    if not params.get("patentId") and not params.get("patentNumber"):
        print(
            "Error: At least one of 'patentId' or 'patentNumber' must be provided.",
            file=sys.stderr,
        )
        sys.exit(1)


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
        with urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        return {"error": f"HTTP {e.code}: {e.reason}", "details": body}
    except URLError as e:
        return {"error": f"Connection failed: {e.reason}"}


def main():
    if len(sys.argv) < 2:
        print("Usage: zhihuiya_fulltext_image.py '<JSON parameters>'", file=sys.stderr)
        print(
            'Example: zhihuiya_fulltext_image.py \'{"patentNumber": "US20230012345A1", "limit": "100"}\'',
            file=sys.stderr,
        )
        sys.exit(1)

    # Parse and validate input parameters
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid parameter format: {e}", file=sys.stderr)
        sys.exit(1)

    validate_params(params)

    # Execute the API call and print results
    result = call_api(params)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
