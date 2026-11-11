#!/usr/bin/env python3
"""Run the named Lazada store operations."""
from _operations import main

API_PATH = "/lazada/store"
SLUG = "linkfox-lazada-store-auth"
OPERATIONS = {
    "getSeller": False,
    "getSellerMetrics": False,
}


if __name__ == "__main__":
    raise SystemExit(main(API_PATH, SLUG, OPERATIONS))
