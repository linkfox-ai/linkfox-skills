#!/usr/bin/env python3
"""
Eureka Patent Description Data Query - LinkFox Skill
Calls the eureka/descriptionData API endpoint to retrieve patent specifications.

Usage:
  python eureka_description.py '{"patentNumber": "CN115099012A"}'
  python eureka_description.py '{"patentId": "abc123", "replaceByRelated": "1"}'
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


API_URL = "https://tool-gateway.linkfox.com/eureka/descriptionData"


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
    has_patent_id = bool(params.get("patentId", "").strip())
    has_patent_number = bool(params.get("patentNumber", "").strip())
    if not has_patent_id and not has_patent_number:
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
        with urlopen(req, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        return {"error": f"HTTP {e.code}: {e.reason}", "details": body}
    except URLError as e:
        return {"error": f"Connection failed: {e.reason}"}


def main():
    if len(sys.argv) < 2:
        print("Usage: eureka_description.py '<JSON parameters>'", file=sys.stderr)
        print(
            "Example: eureka_description.py "
            "'{\"patentNumber\": \"CN115099012A\"}'",
            file=sys.stderr,
        )
        print(
            "\nParameters:",
            file=sys.stderr,
        )
        print(
            "  patentId          - Patent ID (comma-separated for batch, max 100)",
            file=sys.stderr,
        )
        print(
            "  patentNumber      - Publication number (comma-separated for batch, max 100)",
            file=sys.stderr,
        )
        print(
            "  replaceByRelated  - Use family patent description if unavailable: 1=yes, 0=no",
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
