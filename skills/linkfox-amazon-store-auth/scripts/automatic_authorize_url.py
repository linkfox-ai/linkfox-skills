#!/usr/bin/env python3
"""Generate one seller authorization URL from explicit Unicode arguments."""

import argparse
import json
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from authorize_url import API_ENDPOINT, get_api_key


def call_api(params):
    request = Request(
        API_ENDPOINT,
        data=json.dumps(params, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": get_api_key(),
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "LinkFox-Skill/2.0",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=150) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        body = error.read().decode("utf-8") if error.fp else ""
        return {"error": f"HTTP {error.code}: {error.reason}", "details": body}
    except URLError as error:
        return {"error": f"Connection failed: {error.reason}"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--region", choices=("NA", "EU", "FE"), required=True)
    parser.add_argument("--seller-name", required=True)
    parser.add_argument("--central", choices=("seller",), required=True)
    parser.add_argument("--marketplace", required=True)
    args = parser.parse_args()
    if sys.platform.startswith("linux"):
        print(json.dumps({"error": "auto-auth-unsupported-linux"}))
        return 1
    seller_name = args.seller_name.strip()
    marketplace = args.marketplace.strip()
    if not seller_name:
        parser.error("seller-name must be non-empty")
    if not marketplace:
        parser.error("marketplace must be non-empty")
    result = call_api({
        "region": args.region,
        "sellerName": seller_name,
        "central": args.central,
        "marketplace": marketplace,
    })
    print(json.dumps(result, ensure_ascii=False))
    error_code = str(result.get("errcode", ""))
    failed = "error" in result or (
        error_code.isdigit() and int(error_code) not in (0, 200))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
