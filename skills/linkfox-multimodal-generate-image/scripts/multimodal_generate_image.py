#!/usr/bin/env python3
"""
AI Image Generation - LinkFox Skill
Calls the multimodal/generateImage API endpoint

Usage:
  python multimodal_generate_image.py '{"prompt": "A product photo of a red handbag on white background"}'
  python multimodal_generate_image.py '{"prompt": "Change background to blue", "referenceImageUrl": "https://example.com/img.jpg", "aspectRatio": "4:3"}'
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


API_URL = "https://tool-gateway.linkfox.com/multimodal/generateImage"


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
    # prompt is required
    if "prompt" not in params or not params["prompt"].strip():
        print("Error: 'prompt' is a required parameter and cannot be empty.", file=sys.stderr)
        sys.exit(1)

    # Check prompt length
    if len(params["prompt"]) > 1000:
        print("Error: 'prompt' must not exceed 1000 characters.", file=sys.stderr)
        sys.exit(1)

    # Validate aspectRatio if provided
    valid_ratios = {"1:1", "3:4", "4:3", "9:16", "16:9"}
    if "aspectRatio" in params and params["aspectRatio"] not in valid_ratios:
        print(
            f"Error: Invalid aspectRatio '{params['aspectRatio']}'. "
            f"Supported values: {', '.join(sorted(valid_ratios))}",
            file=sys.stderr,
        )
        sys.exit(1)

    # Validate referenceImageUrl count if provided
    if "referenceImageUrl" in params and params["referenceImageUrl"]:
        urls = [u.strip() for u in params["referenceImageUrl"].split(",") if u.strip()]
        if len(urls) > 3:
            print("Error: A maximum of 3 reference image URLs are supported.", file=sys.stderr)
            sys.exit(1)

    # Check referenceImageUrl length
    if "referenceImageUrl" in params and len(params["referenceImageUrl"]) > 1000:
        print("Error: 'referenceImageUrl' must not exceed 1000 characters.", file=sys.stderr)
        sys.exit(1)


def call_api(params: dict) -> dict:
    """Call the tool gateway API and return the parsed response."""
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
        print("Usage: multimodal_generate_image.py '<JSON parameters>'", file=sys.stderr)
        print(
            "Example: multimodal_generate_image.py "
            "'{\"prompt\": \"A product photo of a red handbag on white background\"}'",
            file=sys.stderr,
        )
        print(
            "\nParameters:",
            file=sys.stderr,
        )
        print("  prompt            (required) Text prompt describing the desired image", file=sys.stderr)
        print("  referenceImageUrl (optional) Reference image URL(s), comma-separated, max 3", file=sys.stderr)
        print("  aspectRatio       (optional) 1:1 | 3:4 | 4:3 | 9:16 | 16:9, default 1:1", file=sys.stderr)
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
