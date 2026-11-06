#!/usr/bin/env python3
"""根据列表记录 ID 查询政策资讯全文；支持 JSON 参数、--inline 和 --no-cache。"""

from _policy_feed import run


API_PATH = "/amazon/policyFeedDetail"
SLUG = "linkfox-amazon-policy-feed"


def main(argv=None):
    return run(API_PATH, SLUG, argv)


if __name__ == "__main__":
    raise SystemExit(main())
