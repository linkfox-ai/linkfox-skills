#!/usr/bin/env python3
"""将只读 Ads 授权记录作为单个 JSON 对象返回，不落盘。"""

import argparse
import json
import sys

import authorized_stores
import profiles


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source", choices=("authorized-stores", "profiles"),
        default="authorized-stores")
    args = parser.parse_args()
    result = (authorized_stores.call_api() if args.source == "authorized-stores"
              else profiles.call_api({}))
    print(json.dumps(result, ensure_ascii=False))
    return 0 if "error" not in result else 1


if __name__ == "__main__":
    sys.exit(main())
