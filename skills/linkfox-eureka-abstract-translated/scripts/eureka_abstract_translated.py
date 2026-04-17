#!/usr/bin/env python3
"""
Eureka Patent Abstract (Translated) - LinkFox Skill
Calls the eureka/abstractDataTranslated API endpoint to retrieve
translated patent titles and abstracts.

Usage:
  python eureka_abstract_translated.py '{"patentNumber": "US20200012345A1", "lang": "en"}'
  python eureka_abstract_translated.py '{"patentId": "12345678", "lang": "cn", "replaceByRelated": 1}'
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


API_URL = "https://tool-gateway.linkfox.com/eureka/abstractDataTranslated"


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
    """Validate that at least one patent identifier is provided."""
    if not params.get("patentId") and not params.get("patentNumber"):
        print(
            "Error: At least one of 'patentId' or 'patentNumber' must be provided.",
            file=sys.stderr,
        )
        sys.exit(1)

    lang = params.get("lang")
    if lang and lang not in ("en", "cn", "jp"):
        print(
            f"Error: Unsupported language '{lang}'. Supported values: en, cn, jp.",
            file=sys.stderr,
        )
        sys.exit(1)

    replace = params.get("replaceByRelated")
    if replace is not None and replace not in (0, 1):
        print(
            f"Error: 'replaceByRelated' must be 0 or 1, got {replace}.",
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
        print(
            "Usage: eureka_abstract_translated.py '<JSON parameters>'",
            file=sys.stderr,
        )
        print(
            "Example: eureka_abstract_translated.py "
            "'{\"patentNumber\": \"US20200012345A1\", \"lang\": \"en\"}'",
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
