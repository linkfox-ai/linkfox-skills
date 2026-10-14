#!/usr/bin/env python3
"""Generate one Ads authorization URL from explicit Unicode arguments."""

import argparse
import json
import sys

from authorize_url import call_api


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--region", choices=("NA", "EU", "FE"), required=True)
    parser.add_argument("--account-name", required=True)
    args = parser.parse_args()
    if sys.platform.startswith("linux"):
        print(json.dumps({"error": "auto-auth-unsupported-linux"}))
        return 1
    account_name = args.account_name.strip()
    if not account_name:
        parser.error("account-name must be non-empty")
    result = call_api({"region": args.region, "accountName": account_name})
    print(json.dumps(result, ensure_ascii=False))
    return 0 if "error" not in result else 1


if __name__ == "__main__":
    sys.exit(main())
