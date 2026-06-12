#!/usr/bin/env python3
"""
Multimodal Image Recognition - LinkFox Skill
Calls the multimodal/recognizeImage API endpoint to analyze images.

Usage:
  python multimodal_recognize_image.py '{"imageUrl": "https://example.com/photo.jpg", "requirement": "Describe this image"}'
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


API_URL = "https://tool-gateway.linkfox.com/multimodal/recognizeImage"

# Supported image formats
SUPPORTED_FORMATS = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp")


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
    image_url = params.get("imageUrl")
    if not image_url:
        print("Error: 'imageUrl' is required.", file=sys.stderr)
        sys.exit(1)

    if len(image_url) > 1000:
        print("Error: 'imageUrl' exceeds the maximum length of 1000 characters.", file=sys.stderr)
        sys.exit(1)

    requirement = params.get("requirement", "")
    if requirement and len(requirement) > 1000:
        print("Error: 'requirement' exceeds the maximum length of 1000 characters.", file=sys.stderr)
        sys.exit(1)


def call_api(params: dict) -> dict:
    """Call the tool gateway API for image recognition."""
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
        print("Usage: multimodal_recognize_image.py '<JSON parameters>'", file=sys.stderr)
        print(
            'Example: multimodal_recognize_image.py \'{"imageUrl": "https://example.com/photo.jpg", '
            '"requirement": "Describe the product in this image"}\'',
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid parameter format: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate parameters before calling the API
    validate_params(params)

    result = call_api(params)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
