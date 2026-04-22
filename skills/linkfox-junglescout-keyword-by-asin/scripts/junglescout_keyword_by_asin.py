#!/usr/bin/env python3
"""
Jungle Scout — 根据 ASIN 反查关键词 - LinkFox Skill
Calls the tool-jungle-scout/keywords/by-asin API endpoint

Usage:
  python junglescout_keyword_by_asin.py '{"marketplace": "us", "asins": ["B0DXXXXXXX"], "needCount": 50}'
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


API_URL = "https://tool-gateway.linkfox.com/tool-jungle-scout/keywords/by-asin"

REQUIRED_PARAMS = ["marketplace", "asins"]

VALID_MARKETPLACES = {"us", "uk", "de", "in", "ca", "fr", "it", "es", "mx", "jp"}

MAX_ASINS = 10


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
    """Validate required parameters and constraints."""
    missing = [p for p in REQUIRED_PARAMS if p not in params]
    if missing:
        print(f"Error: missing required parameters: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    marketplace = params.get("marketplace", "")
    if marketplace not in VALID_MARKETPLACES:
        print(
            f"Error: invalid marketplace '{marketplace}'. "
            f"Valid values: {', '.join(sorted(VALID_MARKETPLACES))}",
            file=sys.stderr,
        )
        sys.exit(1)

    asins = params.get("asins", [])
    if not isinstance(asins, list) or len(asins) == 0:
        print("Error: 'asins' must be a non-empty array of ASIN strings", file=sys.stderr)
        sys.exit(1)
    if len(asins) > MAX_ASINS:
        print(f"Error: maximum {MAX_ASINS} ASINs per request, got {len(asins)}", file=sys.stderr)
        sys.exit(1)


def call_api(params: dict) -> dict:
    """Call the tool gateway API."""
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
        print("Usage: junglescout_keyword_by_asin.py '<JSON parameters>'", file=sys.stderr)
        print(
            'Example: junglescout_keyword_by_asin.py \'{"marketplace": "us", '
            '"asins": ["B0DXXXXXXX"], "needCount": 50}\'',
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
