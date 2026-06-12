#!/usr/bin/env python3
"""
Zhihuiya Patent PDF Downloader - LinkFox Skill
Calls the zhihuiya/pdfData API endpoint to retrieve patent PDF download links.

Usage:
  python zhihuiya_pdf_data.py '{"patentNumber": "US20230012345A1"}'
  python zhihuiya_pdf_data.py '{"patentId": "12345678", "replaceByRelated": "1"}'
  python zhihuiya_pdf_data.py '{"patentNumber": "CN115000000A,CN115000001A,CN115000002A"}'
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


API_URL = "https://tool-gateway.linkfox.com/zhihuiya/pdfData"


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

    # Validate batch limit (max 100 entries per field)
    for field_name in ("patentId", "patentNumber"):
        value = params.get(field_name, "").strip()
        if value:
            count = len(value.split(","))
            if count > 100:
                print(
                    f"Error: '{field_name}' contains {count} entries, "
                    f"but the maximum is 100.",
                    file=sys.stderr,
                )
                sys.exit(1)

    # Validate replaceByRelated if present
    replace = params.get("replaceByRelated", "").strip()
    if replace and replace not in ("0", "1"):
        print(
            "Error: 'replaceByRelated' must be '0' or '1'.",
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
        print("Usage: zhihuiya_pdf_data.py '<JSON parameters>'", file=sys.stderr)
        print(
            "Example: zhihuiya_pdf_data.py "
            "'{\"patentNumber\": \"US20230012345A1\"}'",
            file=sys.stderr,
        )
        print(
            "Example: zhihuiya_pdf_data.py "
            "'{\"patentId\": \"12345678\", \"replaceByRelated\": \"1\"}'",
            file=sys.stderr,
        )
        sys.exit(1)

    # Parse the JSON argument
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid parameter format: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate required parameters
    validate_params(params)

    # Call the API and print the result
    result = call_api(params)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
