#!/usr/bin/env python3
"""查询授权申请状态。"""

from _auth import main as run_auth

API_PATH = "/lazada/authorizationStatus"
SLUG = "authorization-status"


def main(argv=None):
    return run_auth(API_PATH, "authorizationStatus", SLUG, argv)


if __name__ == "__main__":
    raise SystemExit(main())
