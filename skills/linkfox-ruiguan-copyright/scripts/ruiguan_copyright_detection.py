#!/usr/bin/env python3
"""
Ruiguan Copyright Detection - LinkFox Skill
Calls the ruiguan/copyrightDetection API endpoint to check images for copyright infringement.

Usage:
  python ruiguan_copyright_detection.py '{"imageUrl": "https://example.com/image.jpg", "topNumber": 100, "enableRadar": true}'
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


API_URL = "https://tool-gateway.linkfox.com/ruiguan/copyrightDetection"


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
    """Validate required parameters and enforce constraints."""
    # imageUrl is required
    if "imageUrl" not in params or not params["imageUrl"]:
        print("Error: 'imageUrl' is required.", file=sys.stderr)
        sys.exit(1)

    if len(params["imageUrl"]) > 1000:
        print("Error: 'imageUrl' must not exceed 1000 characters.", file=sys.stderr)
        sys.exit(1)

    # topNumber: default 100, range 10-200
    if "topNumber" not in params:
        params["topNumber"] = 100
    else:
        top = params["topNumber"]
        if not isinstance(top, int) or top < 10 or top > 200:
            print("Error: 'topNumber' must be an integer between 10 and 200.", file=sys.stderr)
            sys.exit(1)

    # enableRadar: default true
    if "enableRadar" not in params:
        params["enableRadar"] = True

    return params


def call_api(params: dict) -> dict:
    """Call the tool gateway API for copyright detection."""
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
        print("Usage: ruiguan_copyright_detection.py '<JSON parameters>'", file=sys.stderr)
        print(
            'Example: ruiguan_copyright_detection.py \'{"imageUrl": "https://example.com/image.jpg", "topNumber": 100, "enableRadar": true}\'',
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid parameter format: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate and apply defaults
    params = validate_params(params)

    result = call_api(params)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
