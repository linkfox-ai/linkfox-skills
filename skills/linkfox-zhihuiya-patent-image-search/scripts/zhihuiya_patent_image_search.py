#!/usr/bin/env python3
"""
Zhihuiya Patent Image Search - LinkFox Skill
Calls the zhihuiya/patentImageSearch API endpoint to find similar patents by image.

Usage:
  python zhihuiya_patent_image_search.py '<JSON parameters>'

Examples:
  # Design patent search (intelligent association model)
  python zhihuiya_patent_image_search.py '{"url": "https://example.com/product.jpg", "patentType": "D", "model": 1, "limit": 20}'

  # Utility model patent search in China and US
  python zhihuiya_patent_image_search.py '{"url": "https://example.com/product.jpg", "patentType": "U", "model": 4, "country": "CN,US", "limit": 20}'

  # Design patent search with Locarno classification filter
  python zhihuiya_patent_image_search.py '{"url": "https://example.com/product.jpg", "patentType": "D", "model": 1, "loc": "07-01", "limit": 20}'
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


API_URL = "https://tool-gateway.linkfox.com/zhihuiya/patentImageSearch"

# Required parameters for every request
REQUIRED_PARAMS = ["url", "model", "patentType"]

# Valid model IDs per patent type
VALID_MODELS = {
    "D": [1, 2],  # Design patent: 1=intelligent association, 2=search this image
    "U": [3, 4],  # Utility model: 3=match shape, 4=match shape/pattern/color
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
    """Validate that required parameters are present and model matches patent type."""
    # Check required parameters
    missing = [p for p in REQUIRED_PARAMS if p not in params]
    if missing:
        print(
            f"Missing required parameters: {', '.join(missing)}\n"
            f"Required: url (image URL), patentType (D or U), model (search model ID)",
            file=sys.stderr,
        )
        sys.exit(1)

    # Validate patentType
    patent_type = params.get("patentType")
    if patent_type not in VALID_MODELS:
        print(
            f"Invalid patentType '{patent_type}'. Must be 'D' (design) or 'U' (utility model).",
            file=sys.stderr,
        )
        sys.exit(1)

    # Validate model matches patent type
    model = params.get("model")
    if model not in VALID_MODELS[patent_type]:
        valid = ", ".join(str(m) for m in VALID_MODELS[patent_type])
        print(
            f"Invalid model {model} for patentType '{patent_type}'. "
            f"Valid models: {valid}",
            file=sys.stderr,
        )
        sys.exit(1)


def call_api(params: dict) -> dict:
    """Send the search request to the tool gateway API and return the response."""
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
        # Use a longer timeout because image search can be slow
        with urlopen(req, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        return {"error": f"HTTP {e.code}: {e.reason}", "details": body}
    except URLError as e:
        return {"error": f"Connection failed: {e.reason}"}


def format_results(result: dict):
    """Pretty-print the search results for quick review."""
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        if "details" in result:
            print(f"Details: {result['details']}", file=sys.stderr)
        return

    total = result.get("total", 0)
    all_records = result.get("allRecordsCount", total)
    data = result.get("data", [])

    print(f"Results: {total} returned, {all_records} total matches\n")

    for i, patent in enumerate(data, 1):
        score = patent.get("score", "N/A")
        title = patent.get("title", "N/A")
        apno = patent.get("apno", "N/A")
        patent_pn = patent.get("patentPn", "N/A")
        authority = patent.get("authority", "N/A")
        inventor = patent.get("inventor", "N/A")
        assignee = patent.get("currentAssignee") or patent.get("originalAssignee", "N/A")
        loc_list = patent.get("loc", [])
        img_url = patent.get("url", "N/A")

        print(f"--- #{i} (Score: {score}) ---")
        print(f"  Title:       {title}")
        print(f"  App. No:     {apno}")
        print(f"  Patent No:   {patent_pn}")
        print(f"  Authority:   {authority}")
        print(f"  Inventor:    {inventor}")
        print(f"  Assignee:    {assignee}")
        if loc_list:
            print(f"  LOC:         {', '.join(str(x) for x in loc_list)}")
        print(f"  Image:       {img_url}")
        print()


def main():
    if len(sys.argv) < 2:
        print("Usage: zhihuiya_patent_image_search.py '<JSON parameters>'", file=sys.stderr)
        print(
            "\nExample:\n"
            '  zhihuiya_patent_image_search.py \'{"url": "https://example.com/product.jpg", '
            '"patentType": "D", "model": 1, "limit": 20}\'',
            file=sys.stderr,
        )
        print(
            "\nRequired parameters:\n"
            "  url        - Image URL to search against\n"
            "  patentType - D (design patent) or U (utility model patent)\n"
            "  model      - Search model: 1 or 2 for design, 3 or 4 for utility model",
            file=sys.stderr,
        )
        sys.exit(1)

    # Parse JSON input
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid JSON parameter format: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate parameters before calling the API
    validate_params(params)

    # Call the API
    result = call_api(params)

    # Output raw JSON for programmatic consumption
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # Also print a human-readable summary to stderr
    print("\n--- Human-Readable Summary ---", file=sys.stderr)
    import io
    old_stdout = sys.stdout
    sys.stdout = sys.stderr
    format_results(result)
    sys.stdout = old_stdout


if __name__ == "__main__":
    main()
