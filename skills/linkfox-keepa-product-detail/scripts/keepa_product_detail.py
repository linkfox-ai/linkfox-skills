#!/usr/bin/env python3
"""
Keepa Product Request - LinkFox Skill
Calls the keepa/productRequest API endpoint

Usage:
  python keepa_product_request.py '{"asin": "B0088PUEPK", "domain": "1", "history": 1}'
  python keepa_product_request.py '{"asin": "B0088PUEPK,B00U26V4VQ,B07M68S376", "domain": "1"}'
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


API_URL = "https://tool-gateway.linkfox.com/keepa/productRequest"


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
        print("Usage: keepa_product_request.py '<JSON parameters>'", file=sys.stderr)
        print(
            "Example: keepa_product_request.py "
            "'{\"asin\": \"B0088PUEPK\", \"domain\": \"1\", \"history\": 1}'",
            file=sys.stderr,
        )
        print(
            "\nParameters:",
            file=sys.stderr,
        )
        print(
            "  asin    (required) One or more ASINs, comma-separated, max 100",
            file=sys.stderr,
        )
        print(
            "  domain  (required) Marketplace ID: 1=US, 2=UK, 3=DE, 4=FR, 5=JP, 6=CA, 8=IT, 9=ES, 10=IN, 11=MX, 12=BR",
            file=sys.stderr,
        )
        print(
            "  history (optional) 1=include historical sales data, 0=basic info only (default: 0)",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid parameter format: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate required parameters
    if "asin" not in params:
        print("Error: 'asin' parameter is required.", file=sys.stderr)
        sys.exit(1)
    if "domain" not in params:
        print("Error: 'domain' parameter is required.", file=sys.stderr)
        sys.exit(1)

    valid_domains = {"1", "2", "3", "4", "5", "6", "8", "9", "10", "11", "12"}
    if str(params["domain"]) not in valid_domains:
        print(
            f"Error: Invalid domain '{params['domain']}'. "
            f"Valid values: {', '.join(sorted(valid_domains, key=int))}",
            file=sys.stderr,
        )
        sys.exit(1)

    # Ensure domain is a string as required by the API
    params["domain"] = str(params["domain"])

    result = call_api(params)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
