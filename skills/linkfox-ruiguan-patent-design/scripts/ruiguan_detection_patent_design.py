#!/usr/bin/env python3
"""
Ruiguan Design Patent Detection - LinkFox Skill
Calls the ruiguan/detectionPatentDesign API endpoint to check product images
against global design patent databases.

Usage:
  python ruiguan_detection_patent_design.py '{"imageUrl": "https://example.com/product.jpg", "queryMode": "hybrid", "topNumber": 50, "regions": "US"}'
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


API_URL = "https://tool-gateway.linkfox.com/ruiguan/detectionPatentDesign"

# Required parameters that must be present in the request
REQUIRED_PARAMS = ["imageUrl", "queryMode", "topNumber"]

# Default values applied when optional parameters are not provided
DEFAULTS = {
    "queryMode": "hybrid",
    "topNumber": 100,
    "regions": "US",
    "patentStatus": "1",
    "enableRadar": True,
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


def validate_params(params: dict):
    """Validate that all required parameters are present."""
    missing = [p for p in REQUIRED_PARAMS if p not in params]
    if missing:
        print(
            f"Missing required parameters: {', '.join(missing)}\n"
            f"Required: imageUrl (product image URL), queryMode (physical/line/hybrid), topNumber (1-100)",
            file=sys.stderr,
        )
        sys.exit(1)

    # Validate topNumber range
    top_number = params.get("topNumber", 100)
    if not isinstance(top_number, int) or top_number < 1 or top_number > 100:
        print("topNumber must be an integer between 1 and 100", file=sys.stderr)
        sys.exit(1)

    # Validate queryMode value
    query_mode = params.get("queryMode", "hybrid")
    if query_mode not in ("physical", "line", "hybrid"):
        print(
            f"Invalid queryMode: '{query_mode}'. Must be one of: physical, line, hybrid",
            file=sys.stderr,
        )
        sys.exit(1)


def apply_defaults(params: dict) -> dict:
    """Apply default values for optional parameters that are not provided."""
    result = dict(params)
    for key, default_value in DEFAULTS.items():
        if key not in result:
            result[key] = default_value
    return result


def call_api(params: dict) -> dict:
    """Call the Ruiguan design patent detection API."""
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
        # Use a longer timeout since patent detection can be slow
        with urlopen(req, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        return {"error": f"HTTP {e.code}: {e.reason}", "details": body}
    except URLError as e:
        return {"error": f"Connection failed: {e.reason}"}


def summarize_results(result: dict):
    """Print a human-readable summary of high-risk patents."""
    data = result.get("data", [])
    total = result.get("total", 0)

    print(f"\n--- Detection Summary ---")
    print(f"Total patents found: {total}")

    # Filter high-risk patents (similarity >= 0.7 or has TRO history)
    high_risk = []
    for patent in data:
        similarity = float(patent.get("similarity", 0))
        tro_case = patent.get("troCase", False)
        tro_holder = patent.get("troHolder", False)
        if similarity >= 0.7 or tro_case or tro_holder:
            high_risk.append(patent)

    if high_risk:
        print(f"High-risk patents (similarity >= 0.7 or TRO history): {len(high_risk)}")
        print()
        for i, patent in enumerate(high_risk, 1):
            print(f"  [{i}] {patent.get('applicationNumber', 'N/A')}")
            print(f"      Title: {patent.get('patentProd', 'N/A')}")
            print(f"      Title (CN): {patent.get('patentProdCn', 'N/A')}")
            print(f"      Similarity: {patent.get('similarity', 'N/A')}")
            print(f"      TRO Case: {patent.get('troCase', False)}")
            print(f"      TRO Holder: {patent.get('troHolder', False)}")
            radar = patent.get("radarResult", {})
            if radar:
                print(f"      Radar - Suspected Infringement: {radar.get('same', 'N/A')}")
                print(f"      Radar - Explanation: {radar.get('exp', 'N/A')}")
            print()
    else:
        print("No high-risk patents found (none with similarity >= 0.7 or TRO history).")

    print("Note: This detection result is generated by LinkfoxAgent.")
    print("It is recommended to consult a professional IP attorney for legal advice.")


def main():
    if len(sys.argv) < 2:
        print("Usage: ruiguan_detection_patent_design.py '<JSON parameters>'", file=sys.stderr)
        print(
            "Example: ruiguan_detection_patent_design.py "
            "'{\"imageUrl\": \"https://example.com/product.jpg\", \"queryMode\": \"hybrid\", \"topNumber\": 50}'",
            file=sys.stderr,
        )
        print(
            "\nRequired parameters:\n"
            "  imageUrl   - Product image URL\n"
            "  queryMode  - Search mode: physical, line, or hybrid\n"
            "  topNumber  - Number of results (1-100)\n"
            "\nOptional parameters:\n"
            "  regions           - Country codes, e.g., US,EU,CN (default: US)\n"
            "  productTitle      - Product title\n"
            "  productDescription - Product description\n"
            "  patentStatus      - 1 (active), 0 (expired), 1,0 (both) (default: 1)\n"
            "  enableRadar       - Enable radar analysis (default: true)\n"
            "  topLoc            - LOC codes, e.g., 06,07\n"
            "  sourceLanguage    - Source language, e.g., zh-CN",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid parameter format: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate required parameters
    validate_params(params)

    # Apply defaults for optional parameters
    params = apply_defaults(params)

    # Call the API
    result = call_api(params)

    # Print full JSON response
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # If successful and contains data, print a summary
    if "error" not in result and "data" in result:
        summarize_results(result)


if __name__ == "__main__":
    main()
