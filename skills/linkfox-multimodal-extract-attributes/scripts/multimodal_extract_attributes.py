#!/usr/bin/env python3
"""
Multimodal Product Main Image Prompt Extractor - LinkFox Skill
Calls the multimodal/extractPromptsFromMainImage API endpoint

Usage:
  python multimodal_extract_prompts.py '<JSON parameters>'

Example:
  python multimodal_extract_prompts.py '{"productImageAnalysisPrompt": "Extract the dominant color of each product", "refResultData": "{\"products\":[{\"asin\":\"B0XXXXXXXX\",\"imageUrl\":\"https://example.com/img.jpg\"}]}"}'
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


API_URL = "https://tool-gateway.linkfox.com/multimodal/extractPromptsFromMainImage"


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
    """Call the multimodal image analysis API endpoint."""
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
        # Use a longer timeout since image analysis can take time
        with urlopen(req, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        return {"error": f"HTTP {e.code}: {e.reason}", "details": body}
    except URLError as e:
        return {"error": f"Connection failed: {e.reason}"}


def main():
    if len(sys.argv) < 2:
        print("Usage: multimodal_extract_prompts.py '<JSON parameters>'", file=sys.stderr)
        print(
            "Example: multimodal_extract_prompts.py "
            "'{\"productImageAnalysisPrompt\": \"Extract the dominant color\", "
            "\"refResultData\": \"{\\\"products\\\":[{\\\"asin\\\":\\\"B0XXXXXXXX\\\","
            "\\\"imageUrl\\\":\\\"https://example.com/img.jpg\\\"}]}\"}'",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid parameter format: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate that the required parameter is present
    if "productImageAnalysisPrompt" not in params:
        print(
            "Error: 'productImageAnalysisPrompt' is required. "
            "Provide a natural language instruction describing what to extract from images.",
            file=sys.stderr,
        )
        sys.exit(1)

    result = call_api(params)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
