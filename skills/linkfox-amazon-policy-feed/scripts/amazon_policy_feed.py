#!/usr/bin/env python3
"""查询亚马逊政策资讯列表；支持 JSON 参数、--inline 和 --no-cache。"""

from _policy_feed import run


API_PATH = "/amazon/policyFeed"
SLUG = "linkfox-amazon-policy-feed"


def main(argv=None):
    return run(API_PATH, SLUG, argv)


if __name__ == "__main__":
    raise SystemExit(main())
