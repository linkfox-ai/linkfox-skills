#!/usr/bin/env python3
"""发起店铺授权。"""

from _auth import main as run_auth

API_PATH = "/lazada/authorizeUrl"
SLUG = "authorize-url"


def main(argv=None):
    return run_auth(API_PATH, "authorizeUrl", SLUG, argv)


if __name__ == "__main__":
    raise SystemExit(main())
