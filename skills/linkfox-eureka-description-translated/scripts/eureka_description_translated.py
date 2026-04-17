#!/usr/bin/env python3
"""
Eureka Patent Description (Translated) - LinkFox Skill
Calls the eureka/descriptionDataTranslated API endpoint to retrieve
translated patent description text.

Usage:
  python eureka_description_translated.py '{"patentNumber": "US10123456B2", "lang": "en"}'
  python eureka_description_translated.py '{"patentId": "abc123", "lang": "cn", "replaceByRelated": 1}'
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


API_URL = "https://tool-gateway.linkfox.com/eureka/descriptionDataTranslated"


def get_api_key():
    """Retrieve the API key from environment, with a friendly prompt if missing."""
    key = os.environ.get("LINKFOXAGENT_API_KEY")
    if not key:
        print(
            "API Key not configured. Please complete authorization first:\n"
            "1. Visit https://yxgb3sicy7.feishu.cn/wiki/GIkkweGghiyzkqkRXQKc2n0Tnre to obtain your Key\n"
            "2. Set the environment variable: export LINKFOXAGENT_API_KEY=your-key-here",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


def validate_params(params: dict):
    """Validate that at least one of patentId or patentNumber is provided."""
    has_patent_id = params.get("patentId", "").strip() if isinstance(params.get("patentId"), str) else False
    has_patent_number = params.get("patentNumber", "").strip() if isinstance(params.get("patentNumber"), str) else False

    if not has_patent_id and not has_patent_number:
        print(
            "Error: At least one of 'patentId' or 'patentNumber' must be provided.",
            file=sys.stderr,
        )
        sys.exit(1)

    lang = params.get("lang", "en")
    if lang not in ("en", "cn", "jp"):
        print(
            f"Error: Invalid lang '{lang}'. Supported values: en, cn, jp",
            file=sys.stderr,
        )
        sys.exit(1)

    replace = params.get("replaceByRelated")
    if replace is not None and replace not in (0, 1):
        print(
            f"Error: Invalid replaceByRelated '{replace}'. Must be 0 or 1.",
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
        with urlopen(req, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        return {"error": f"HTTP {e.code}: {e.reason}", "details": body}
    except URLError as e:
        return {"error": f"Connection failed: {e.reason}"}


def main():
    if len(sys.argv) < 2:
        print("Usage: eureka_description_translated.py '<JSON parameters>'", file=sys.stderr)
        print(
            'Example: eureka_description_translated.py \'{"patentNumber": "US10123456B2", "lang": "en"}\'',
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
