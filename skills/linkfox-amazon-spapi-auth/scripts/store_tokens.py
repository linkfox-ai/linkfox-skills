#!/usr/bin/env python3
"""
SP-API Store Tokens Query - LinkFox Skill
Calls the /spApi/storeTokens endpoint to get store tokens

Usage:
  python store_tokens.py '{"sellerId": "A1234567890", "region": "NA"}'
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


API_BASE_URL = os.environ.get("SPAPI_BASE_URL", "https://tool-gateway.linkfox.com")
API_ENDPOINT = f"{API_BASE_URL}/spApi/storeTokens"


def get_api_key():
    """Retrieve the API key from environment, with a friendly prompt if missing."""
    key = os.environ.get("LINKFOXAGENT_API_KEY")
    if not key:
        print(
            "API Key not configured. Please set the environment variable:\n"
            "  export LINKFOXAGENT_API_KEY=your-key-here",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


def call_api(params: dict) -> dict:
    """Call the store tokens API."""
    api_key = get_api_key()
    data = json.dumps(params).encode("utf-8")

    req = Request(
        API_ENDPOINT,
        data=data,
        headers={
            "Authorization": api_key,
            "Content-Type": "application/json",
            "User-Agent": "LinkFox-Skill/1.0",
        },
        method="POST",
    )

    try:
        with urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        return {"error": f"HTTP {e.code}: {e.reason}", "details": body}
    except URLError as e:
        return {"error": f"Connection failed: {e.reason}"}


def main():
    if len(sys.argv) < 2:
        print("Usage: store_tokens.py '<JSON parameters>'", file=sys.stderr)
        print(
            'Example: store_tokens.py \'{"sellerId": "A1234567890", "region": "NA"}\'',
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid parameter format: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate required fields
    if "sellerId" not in params or "region" not in params:
        print("Error: Both 'sellerId' and 'region' parameters are required", file=sys.stderr)
        sys.exit(1)

    result = call_api(params)

    # Mask tokens in output for security
    if "accessToken" in result:
        result["accessToken"] = result["accessToken"][:10] + "..." if len(result["accessToken"]) > 10 else result["accessToken"]
    if "refreshToken" in result:
        result["refreshToken"] = result["refreshToken"][:10] + "..." if len(result["refreshToken"]) > 10 else result["refreshToken"]

    print(json.dumps(result, indent=2, ensure_ascii=False))

    # If successful, print helpful info
    if "expiresIn" in result:
        expires_in = result.get("expiresIn", "0")
        print(f"\n✓ Tokens retrieved successfully", file=sys.stderr)
        print(f"Token expires in: {expires_in} seconds", file=sys.stderr)
        print("Note: Tokens have been masked for security.", file=sys.stderr)


if __name__ == "__main__":
    main()
