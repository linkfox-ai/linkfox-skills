#!/usr/bin/env python3
"""
Ruiguan Utility Patent Detection - LinkFox Skill
Calls the ruiguan/utilityPatentDetection API endpoint to search for
similar utility (invention) patents based on product information.

Usage:
  python ruiguan_utility_patent_detection.py '<JSON parameters>'

Example:
  python ruiguan_utility_patent_detection.py '{
    "productTitle": "Portable USB-C Fast Charger 65W GaN",
    "productDescription": "A compact 65W GaN USB-C fast charger with foldable prongs, supporting PD3.0 and QC4.0.",
    "region": "US",
    "topNumber": 100
  }'
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


API_URL = "https://tool-gateway.linkfox.com/ruiguan/utilityPatentDetection"

# Required parameters for the API call
REQUIRED_PARAMS = ["productTitle", "productDescription", "region", "topNumber"]

# Default values applied when optional params are missing
DEFAULTS = {
    "region": "US",
    "topNumber": 100,
}


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


def validate_params(params: dict) -> dict:
    """Validate and apply defaults to request parameters."""
    # Apply defaults for missing optional fields
    for key, default_val in DEFAULTS.items():
        if key not in params:
            params[key] = default_val

    # Check required parameters
    missing = [p for p in REQUIRED_PARAMS if p not in params]
    if missing:
        print(
            f"Missing required parameters: {', '.join(missing)}\n"
            f"Required: productTitle, productDescription, region, topNumber",
            file=sys.stderr,
        )
        sys.exit(1)

    # Validate topNumber range (10--200)
    top = params.get("topNumber", 100)
    if not isinstance(top, int) or top < 10 or top > 200:
        print(
            "topNumber must be an integer between 10 and 200.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Validate string length limits
    for field in ("productTitle", "productDescription", "region"):
        val = params.get(field, "")
        if isinstance(val, str) and len(val) > 1000:
            print(
                f"{field} exceeds the maximum length of 1000 characters.",
                file=sys.stderr,
            )
            sys.exit(1)

    return params


def call_api(params: dict) -> dict:
    """Send a POST request to the utility patent detection API."""
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
            "Usage: ruiguan_utility_patent_detection.py '<JSON parameters>'\n"
            "\n"
            "Example:\n"
            '  ruiguan_utility_patent_detection.py \'{"productTitle": "Portable USB-C Charger", '
            '"productDescription": "65W GaN charger with PD3.0", "region": "US", "topNumber": 100}\'',
            file=sys.stderr,
        )
        sys.exit(1)

    # Parse the JSON argument
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid JSON parameter format: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate and apply defaults
    params = validate_params(params)

    # Call the API and print the result
    result = call_api(params)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
