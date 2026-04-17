#!/usr/bin/env python3
"""
Eureka Patent Image Search - LinkFox Skill
Calls the eureka/patentImageSearch API endpoint to find visually similar patents.

Usage:
  python eureka_patent_image_search.py '{"url": "https://example.com/img.jpg", "model": 1, "patentType": "D"}'
  python eureka_patent_image_search.py '{"url": "https://example.com/img.jpg", "model": 3, "patentType": "U", "country": "CN,US", "limit": 20}'
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


API_URL = "https://tool-gateway.linkfox.com/eureka/patentImageSearch"

VALID_MODELS = {1, 2, 3, 4}
VALID_PATENT_TYPES = {"D", "U"}


def get_api_key():
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
    url = params.get("url", "").strip()
    if not url:
        print("Error: 'url' (image URL) is required.", file=sys.stderr)
        sys.exit(1)

    model = params.get("model")
    if model is None:
        print("Error: 'model' is required (1/2/3/4).", file=sys.stderr)
        sys.exit(1)
    if int(model) not in VALID_MODELS:
        print(
            f"Error: 'model' must be one of {sorted(VALID_MODELS)}, got {model}.",
            file=sys.stderr,
        )
        sys.exit(1)

    patent_type = params.get("patentType", "").strip()
    if not patent_type:
        print('Error: \'patentType\' is required ("D" or "U").', file=sys.stderr)
        sys.exit(1)
    if patent_type not in VALID_PATENT_TYPES:
        print(
            f"Error: 'patentType' must be one of {sorted(VALID_PATENT_TYPES)}, got '{patent_type}'.",
            file=sys.stderr,
        )
        sys.exit(1)


def call_api(params: dict) -> dict:
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
        print(
            "Usage: eureka_patent_image_search.py '<JSON parameters>'",
            file=sys.stderr,
        )
        print("Examples:", file=sys.stderr)
        print(
            '  eureka_patent_image_search.py \'{"url": "https://example.com/img.jpg", "model": 1, "patentType": "D"}\'',
            file=sys.stderr,
        )
        print(
            '  eureka_patent_image_search.py \'{"url": "https://example.com/img.jpg", "model": 3, "patentType": "U", "limit": 20}\'',
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
