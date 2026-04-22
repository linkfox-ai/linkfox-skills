#!/usr/bin/env python3
"""
Jungle Scout — 根据关键词扩展关键词信息 (Keyword by Keyword) - LinkFox Skill
Calls the tool-jungle-scout/keywords/by-keyword API endpoint

Usage:
  python junglescout_keyword_by_keyword.py '{"marketplace": "us", "searchTerms": "yoga mat"}'
  python junglescout_keyword_by_keyword.py '{"marketplace": "us", "searchTerms": "yoga mat", "needCount": 50, "minWordCount": 3}'
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


API_URL = "https://tool-gateway.linkfox.com/tool-jungle-scout/keywords/by-keyword"

REQUIRED_PARAMS = ["marketplace", "searchTerms"]

VALID_MARKETPLACES = {"us", "uk", "de", "in", "ca", "fr", "it", "es", "mx", "jp"}

VALID_SORT_VALUES = {
    "name", "-name",
    "dominant_category", "-dominant_category",
    "monthly_trend", "-monthly_trend",
    "quarterly_trend", "-quarterly_trend",
    "monthly_search_volume_exact", "-monthly_search_volume_exact",
    "monthly_search_volume_broad", "-monthly_search_volume_broad",
    "recommended_promotions", "-recommended_promotions",
    "sp_brand_ad_bid", "-sp_brand_ad_bid",
    "ppc_bid_broad", "-ppc_bid_broad",
    "ppc_bid_exact", "-ppc_bid_exact",
    "ease_of_ranking_score", "-ease_of_ranking_score",
    "relevancy_score", "-relevancy_score",
    "organic_product_count", "-organic_product_count",
}


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
    """Validate required and optional parameters."""
    missing = [p for p in REQUIRED_PARAMS if p not in params]
    if missing:
        print(f"Error: missing required parameters: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    mp = params.get("marketplace", "")
    if mp not in VALID_MARKETPLACES:
        print(
            f"Error: invalid marketplace '{mp}'. Must be one of: {', '.join(sorted(VALID_MARKETPLACES))}",
            file=sys.stderr,
        )
        sys.exit(1)

    if "sort" in params and params["sort"] not in VALID_SORT_VALUES:
        print(
            f"Error: invalid sort value '{params['sort']}'. See references/api.md for valid values.",
            file=sys.stderr,
        )
        sys.exit(1)


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
        print("Usage: junglescout_keyword_by_keyword.py '<JSON parameters>'", file=sys.stderr)
        print(
            'Example: junglescout_keyword_by_keyword.py \'{"marketplace": "us", "searchTerms": "yoga mat"}\'',
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
