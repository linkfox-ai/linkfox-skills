#!/usr/bin/env python3
"""
Zhihuiya Patent Claims Data Query - LinkFox Skill
Calls the zhihuiya/claimData API endpoint to retrieve patent claims.

Usage:
  python zhihuiya_claim_data.py '{"patentNumber": "CN115000000A"}'
  python zhihuiya_claim_data.py '{"patentNumber": "CN115000000A,US20230001234A1", "replaceByRelated": "1"}'
  python zhihuiya_claim_data.py '{"patentId": "98a1b2c3-xxxx-xxxx-xxxx-xxxxxxxxxxxx"}'
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


API_URL = "https://tool-gateway.linkfox.com/zhihuiya/claimData"


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
    """Validate that at least one of patentId or patentNumber is provided."""
    if not params.get("patentId") and not params.get("patentNumber"):
        print(
            "Error: At least one of 'patentId' or 'patentNumber' must be provided.",
            file=sys.stderr,
        )
        sys.exit(1)


def call_api(params: dict) -> dict:
    """Call the Zhihuiya claimData API via the LinkFox tool gateway."""
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
        print("Usage: zhihuiya_claim_data.py '<JSON parameters>'", file=sys.stderr)
        print(
            "Example: zhihuiya_claim_data.py "
            "'{\"patentNumber\": \"CN115000000A\"}'",
            file=sys.stderr,
        )
        print(
            "\nAt least one of 'patentId' or 'patentNumber' must be provided.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid parameter format: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate required parameters before calling the API
    validate_params(params)

    result = call_api(params)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
