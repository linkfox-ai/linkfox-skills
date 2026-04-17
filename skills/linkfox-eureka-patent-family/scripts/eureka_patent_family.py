#!/usr/bin/env python3
"""
Eureka Patent Family Query - LinkFox Skill
Calls the eureka/patentFamily API endpoint to retrieve patent family information.

Usage:
  python eureka_patent_family.py '{"patentNumber": "US10000001B2"}'
  python eureka_patent_family.py '{"patentId": "5af83e12-xxxx-xxxx-xxxx-xxxxxxxxxxxx"}'
  python eureka_patent_family.py '{"patentNumber": "US10000001B2,EP3000001A1,CN112345678A"}'
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


API_URL = "https://tool-gateway.linkfox.com/eureka/patentFamily"


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
    if not params.get("patentId") and not params.get("patentNumber"):
        print(
            "Error: At least one of 'patentId' or 'patentNumber' must be provided.",
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
        with urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        return {"error": f"HTTP {e.code}: {e.reason}", "details": body}
    except URLError as e:
        return {"error": f"Connection failed: {e.reason}"}


def main():
    if len(sys.argv) < 2:
        print("Usage: eureka_patent_family.py '<JSON parameters>'", file=sys.stderr)
        print(
            "Examples:",
            file=sys.stderr,
        )
        print(
            '  eureka_patent_family.py \'{"patentNumber": "US10000001B2"}\'',
            file=sys.stderr,
        )
        print(
            '  eureka_patent_family.py \'{"patentId": "5af83e12-xxxx-xxxx-xxxx-xxxxxxxxxxxx"}\'',
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
