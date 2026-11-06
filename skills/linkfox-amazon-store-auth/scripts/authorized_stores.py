#!/usr/bin/env python3
"""Amazon 店铺授权：authorizedStores，保留 JSON CLI 和程序调用入口。"""
import sys
from _auth_common import get_api_base, invoke, run_json
from call_api import get_api_key

API_BASE_URL = get_api_base()


def call_api():
    result, _ok = invoke('authorizedStores', {}, machine=True)
    return result


def main():
    return run_json('authorizedStores')


if __name__ == '__main__':
    sys.exit(main())
