#!/usr/bin/env python3
"""
Zhihuiya Patent Forward Citation - LinkFox Skill
Calls the zhihuiya/patentForwardCitation API endpoint to retrieve
patents and non-patent literature cited by a given patent.

Usage:
  python zhihuiya_forward_citation.py '{"patentNumber": "US10000000B2"}'
  python zhihuiya_forward_citation.py '{"patentId": "12345678"}'
  python zhihuiya_forward_citation.py '{"patentNumber": "US10000000B2,US9876543B1"}'
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


API_URL = "https://tool-gateway.linkfox.com/zhihuiya/patentForwardCitation"


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
    has_patent_id = bool(params.get("patentId", "").strip())
    has_patent_number = bool(params.get("patentNumber", "").strip())
    if not has_patent_id and not has_patent_number:
        print(
            "Error: At least one of 'patentId' or 'patentNumber' must be provided.",
            file=sys.stderr,
        )
        sys.exit(1)


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
        print("Usage: zhihuiya_forward_citation.py '<JSON parameters>'", file=sys.stderr)
        print(
            "Example: zhihuiya_forward_citation.py "
            "'{\"patentNumber\": \"US10000000B2\"}'",
            file=sys.stderr,
        )
        sys.exit(1)

    # Parse the JSON argument
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid parameter format: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate that required parameters are present
    validate_params(params)

    # Call the API and print the result
    result = call_api(params)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
