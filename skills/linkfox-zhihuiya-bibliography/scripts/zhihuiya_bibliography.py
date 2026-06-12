#!/usr/bin/env python3
"""
Zhihuiya Patent Bibliography Query - LinkFox Skill
Calls the zhihuiya/bibliography API endpoint to retrieve patent bibliographic data.

Usage:
  python zhihuiya_bibliography.py '{"patentNumber": "US10123456B2"}'
  python zhihuiya_bibliography.py '{"patentId": "some-patent-id"}'
  python zhihuiya_bibliography.py '{"patentNumber": "US10123456B2,CN112345678A"}'
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


API_URL = "https://tool-gateway.linkfox.com/zhihuiya/bibliography"


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
    """Ensure at least one of patentId or patentNumber is provided."""
    patent_id = params.get("patentId", "").strip()
    patent_number = params.get("patentNumber", "").strip()

    if not patent_id and not patent_number:
        print(
            "Error: At least one of 'patentId' or 'patentNumber' must be provided.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Warn if the count exceeds the 100-patent limit
    for field_name, value in [("patentId", patent_id), ("patentNumber", patent_number)]:
        if value:
            count = len(value.split(","))
            if count > 100:
                print(
                    f"Warning: {field_name} contains {count} entries, "
                    f"but the API supports a maximum of 100 per request.",
                    file=sys.stderr,
                )


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
        print("Usage: zhihuiya_bibliography.py '<JSON parameters>'", file=sys.stderr)
        print(
            "Examples:",
            file=sys.stderr,
        )
        print(
            '  zhihuiya_bibliography.py \'{"patentNumber": "US10123456B2"}\'',
            file=sys.stderr,
        )
        print(
            '  zhihuiya_bibliography.py \'{"patentId": "some-patent-id"}\'',
            file=sys.stderr,
        )
        print(
            '  zhihuiya_bibliography.py \'{"patentNumber": "US10123456B2,CN112345678A"}\'',
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
