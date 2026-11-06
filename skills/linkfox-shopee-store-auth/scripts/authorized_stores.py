#!/usr/bin/env python3
"""列出当前用户已授权的 Shopee 店铺，分别展示 ERP 与 AD 记录。"""

import sys

from _shopee_auth_common import displayed_app_type, read_params, run_request


def call_api():
    return run_request("/shopee/authorizedStores", "authorized-stores", {})


def main():
    params = read_params(
        "用法：python authorized_stores.py ['{}'] [--inline] [--no-cache]",
        optional=True,
    )
    if params:
        print("已授权列表不接受业务参数，请传空对象或不传 JSON。", file=sys.stderr)
        raise SystemExit(1)
    result = call_api()
    if isinstance(result.get("stores"), list):
        print(f"\n已找到 {result.get('total', 0)} 条授权记录：", file=sys.stderr)
        for store in result["stores"]:
            print(
                f"  - shopId={store.get('shopId')}  {store.get('shopName', 'N/A')}  "
                f"merchantId={store.get('merchantId', '')}  region={store.get('region', '')}  "
                f"appType={displayed_app_type(store)}",
                file=sys.stderr,
            )
        print("请同时匹配店铺身份和应用类型；ERP 与 AD 授权不能互相替代。", file=sys.stderr)


if __name__ == "__main__":
    main()
