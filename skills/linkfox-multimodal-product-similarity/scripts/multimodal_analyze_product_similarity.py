#!/usr/bin/env python3
"""
Multimodal Product Image Similarity Analysis - LinkFox Skill
Calls the multimodal/analyzeProductSimilarity API endpoint

Usage:
  python multimodal_analyze_product_similarity.py '<JSON parameters>'

Examples:
  # Basic similarity analysis with default threshold (60)
  python multimodal_analyze_product_similarity.py '{"refResultData": "{\"products\":[...]}", "userInput": "Group by visual similarity"}'

  # Strict matching, cross-brand only
  python multimodal_analyze_product_similarity.py '{"similarityThreshold": 85, "includeSingleBrandGroups": false, "refResultData": "{\"products\":[...]}"}'
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


API_URL = "https://tool-gateway.linkfox.com/multimodal/analyzeProductSimilarity"


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
    """Validate request parameters before sending to the API."""
    threshold = params.get("similarityThreshold")
    if threshold is not None:
        if not isinstance(threshold, int) or threshold < 0 or threshold > 100:
            print(
                "Error: similarityThreshold must be an integer between 0 and 100.",
                file=sys.stderr,
            )
            sys.exit(1)

    include_single = params.get("includeSingleBrandGroups")
    if include_single is not None and not isinstance(include_single, bool):
        print(
            "Error: includeSingleBrandGroups must be a boolean (true/false).",
            file=sys.stderr,
        )
        sys.exit(1)

    # Validate that refResultData, if present, is valid JSON containing products
    ref_data = params.get("refResultData")
    if ref_data is not None:
        try:
            parsed = json.loads(ref_data)
            if not isinstance(parsed, dict) or "products" not in parsed:
                print(
                    "Warning: refResultData should be a JSON object containing a 'products' array.",
                    file=sys.stderr,
                )
        except (json.JSONDecodeError, TypeError):
            print(
                "Warning: refResultData is not valid JSON. The API may reject this request.",
                file=sys.stderr,
            )


def call_api(params: dict) -> dict:
    """Call the tool gateway API for product image similarity analysis."""
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
        # Longer timeout for image analysis which can be compute-intensive
        with urlopen(req, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        return {"error": f"HTTP {e.code}: {e.reason}", "details": body}
    except URLError as e:
        return {"error": f"Connection failed: {e.reason}"}


def print_summary(result: dict):
    """Print a human-readable summary of the analysis result."""
    analysis_info = result.get("analysisInfo", {})
    groups = result.get("groups", [])

    if analysis_info:
        print("\n--- Analysis Summary ---")
        print(f"  Products analyzed : {analysis_info.get('totalProductsAnalyzed', 'N/A')}")
        print(f"  Groups found      : {analysis_info.get('totalGroupsFound', 'N/A')}")
        print(f"  Similarity threshold: {analysis_info.get('similarityThreshold', 'N/A')}")
        print(f"  Timestamp         : {analysis_info.get('analysisTimestamp', 'N/A')}")

    if groups:
        print(f"\n--- Similarity Groups ({len(groups)}) ---")
        for group in groups:
            group_num = group.get("groupNumber", "?")
            reason = group.get("reason", "")
            brand_count = group.get("brandCount", 0)
            asins = group.get("asins", [])
            print(f"\n  Group {group_num} ({len(asins)} products, {brand_count} brands)")
            print(f"  Reason: {reason}")
            for item in asins:
                asin = item.get("asin", "N/A")
                brand = item.get("brand", "N/A")
                price = item.get("price", "N/A")
                print(f"    - {asin}  brand={brand}  price={price}")


def main():
    if len(sys.argv) < 2:
        print(
            "Usage: multimodal_analyze_product_similarity.py '<JSON parameters>'",
            file=sys.stderr,
        )
        print(
            "Example: multimodal_analyze_product_similarity.py "
            "'{\"similarityThreshold\": 60, \"refResultData\": \"{\\\"products\\\":[...]}\", "
            "\"userInput\": \"Group by visual similarity\"}'",
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

    # Print full JSON response
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # If successful and contains groups, also print a human-readable summary
    if "error" not in result and result.get("groups"):
        print_summary(result)


if __name__ == "__main__":
    main()
