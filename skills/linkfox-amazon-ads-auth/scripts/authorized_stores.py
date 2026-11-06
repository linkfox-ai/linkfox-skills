#!/usr/bin/env python3
"""
Amazon Ads 已授权账号与站点列表脚本。
通过公共调用器读取当前成员的授权信息。

用法：
  python authorized_stores.py
"""

import json
import os
import sys

from _ads_auth_common import request, cli_params

# 生产默认走 tool-gateway.linkfox.com；开发/测试期可 export AMAZON_ADS_BASE_URL=<url> 覆盖
API_BASE_URL = (os.environ.get("LINKFOX_TOOL_GATEWAY") or os.environ.get("AMAZON_ADS_BASE_URL") or "https://tool-gateway.linkfox.com").rstrip("/")


def call_api() -> dict:
    """自动核验兼容入口；不落盘，只返回 JSON 对象。"""
    return request("/amazonAds/authorizedStores", {})


def main():
    try:
        params = cli_params(sys.argv[1:])
        params = {}  # 已授权列表不接受业务参数
    except ValueError as e:
        print(f"参数格式错误：{e}", file=sys.stderr)
        sys.exit(1)
    result = request("/amazonAds/authorizedStores", params, persist=True,
                     inline="--inline" in sys.argv[1:])
    if result.get("error"):
        sys.exit(1)

    if "stores" in result:
        stores = result.get("stores", [])
        total = result.get("total", 0)
        print(f"\n✓ 已找到 {total} 条已授权账号与站点：", file=sys.stderr)
        for s in stores:
            print(
                f"  - profileId={s.get('profileId')}  {s.get('accountInfoName', 'N/A')}  "
                f"{s.get('countryCode', '')} ({s.get('region', '')})  "
                f"marketplace={s.get('marketplaceStringId', '')}",
                file=sys.stderr,
            )


if __name__ == "__main__":
    main()
