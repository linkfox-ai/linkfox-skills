#!/usr/bin/env python3
"""
Jungle Scout — ASIN 销售估算 - LinkFox Skill
Calls the tool-jungle-scout/sales-estimates/query API endpoint

Usage:
  python junglescout_sales_estimates.py '{"marketplace": "us", "asin": "B0CXXX1234", "startDate": "2026-03-01", "endDate": "2026-03-31"}'
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


API_URL = "https://tool-gateway.linkfox.com/tool-jungle-scout/sales-estimates/query"

REQUIRED_PARAMS = ["marketplace", "asin", "startDate", "endDate"]

VALID_MARKETPLACES = {"us", "uk", "de", "in", "ca", "fr", "it", "es", "mx", "jp"}


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
    """Validate all required parameters."""
    missing = [p for p in REQUIRED_PARAMS if p not in params]
    if missing:
        print(f"Error: missing required parameters: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    mp = params["marketplace"]
    if mp not in VALID_MARKETPLACES:
        print(
            f"Error: invalid marketplace '{mp}'. "
            f"Valid values: {', '.join(sorted(VALID_MARKETPLACES))}",
            file=sys.stderr,
        )
        sys.exit(1)

    for date_field in ("startDate", "endDate"):
        val = params[date_field]
        if len(val) != 10 or val[4] != "-" or val[7] != "-":
            print(f"Error: {date_field} must be in YYYY-MM-DD format, got '{val}'", file=sys.stderr)
            sys.exit(1)

    if params["endDate"] >= _today():
        print("Error: endDate must be before the current date", file=sys.stderr)
        sys.exit(1)

    if params["startDate"] > params["endDate"]:
        print("Error: startDate must be before or equal to endDate", file=sys.stderr)
        sys.exit(1)


def _today() -> str:
    """Return today's date as YYYY-MM-DD without importing datetime."""
    import time
    t = time.localtime()
    return f"{t.tm_year:04d}-{t.tm_mon:02d}-{t.tm_mday:02d}"


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
        with urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        return {"error": f"HTTP {e.code}: {e.reason}", "details": body}
    except URLError as e:
        return {"error": f"Connection failed: {e.reason}"}


def main():
    if len(sys.argv) < 2:
        print("Usage: junglescout_sales_estimates.py '<JSON parameters>'", file=sys.stderr)
        print(
            'Example: junglescout_sales_estimates.py \'{"marketplace": "us", "asin": "B0CXXX1234", '
            '"startDate": "2026-03-01", "endDate": "2026-03-31"}\'',
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
