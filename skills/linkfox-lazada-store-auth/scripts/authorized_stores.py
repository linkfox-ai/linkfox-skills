#!/usr/bin/env python3
"""列出已连接店铺。"""

from _auth import main as run_auth

API_PATH = "/lazada/authorizedStores"
SLUG = "authorized-stores"


def main(argv=None):
    return run_auth(API_PATH, "authorizedStores", SLUG, argv)


if __name__ == "__main__":
    raise SystemExit(main())
