#!/usr/bin/env python3
"""
SellerSprite Traffic Keyword - LinkFox Skill
Calls sellersprite/traffic/keyword to query traffic keyword lists by ASIN.

Usage:
  python sellersprite_traffic_keyword.py '{"marketplace": "US", "asin": "B0XXXXXXXXX", "page": 1, "size": 50}'
"""

import json
import os
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

API_URL = "https://tool-gateway.linkfox.com/sellersprite/traffic/keyword"


def get_api_key() -> str:
    key = os.environ.get("LINKFOXAGENT_API_KEY")
    if not key:
        print(
            "API Key not configured. Please complete authorization first:\n"
            "1. Visit https://yxgb3sicy7.feishu.cn/wiki/GIkkweGghiyzkqkRXQKc2n0Tnre to obtain your Key\n"
            "2. Set environment variable: export LINKFOXAGENT_API_KEY=your-key-here",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


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
        with urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        return {"error": f"HTTP {e.code}: {e.reason}", "details": body}
    except URLError as e:
        return {"error": f"Connection failed: {e.reason}"}


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: sellersprite_traffic_keyword.py '<JSON parameters>'", file=sys.stderr)
        print(
            "Example: sellersprite_traffic_keyword.py "
            "'{\"marketplace\": \"US\", \"asin\": \"B0XXXXXXXXX\", \"page\": 1, \"size\": 50}'",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid parameter format: {e}", file=sys.stderr)
        sys.exit(1)

    result = call_api(params)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
