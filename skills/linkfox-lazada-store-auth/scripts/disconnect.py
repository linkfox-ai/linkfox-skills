#!/usr/bin/env python3
"""解除当前用户的店铺连接。"""

from _auth import main as run_auth

API_PATH = "/lazada/disconnect"
SLUG = "disconnect"


def main(argv=None):
    return run_auth(API_PATH, "disconnect", SLUG, argv)


if __name__ == "__main__":
    raise SystemExit(main())
