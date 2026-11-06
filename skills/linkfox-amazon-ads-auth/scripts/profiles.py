#!/usr/bin/env python3
"""
Amazon Ads profile 列表脚本。
默认读取数据库快照；refresh=true 时穿透上游刷新。

用法：
  python profiles.py                          # 读取数据库快照
  python profiles.py '{"refresh": true}'      # 从上游 v2/profiles 刷新
"""

import json
import os
import sys

from _ads_auth_common import request, cli_params

# 生产默认走 tool-gateway.linkfox.com；开发/测试期可 export AMAZON_ADS_BASE_URL=<url> 覆盖
API_BASE_URL = (os.environ.get("LINKFOX_TOOL_GATEWAY") or os.environ.get("AMAZON_ADS_BASE_URL") or "https://tool-gateway.linkfox.com").rstrip("/")


def call_api(params: dict) -> dict:
    """自动核验兼容入口；不落盘，只返回 JSON 对象。"""
    return request("/amazonAds/profiles", params)


def main():
    try:
        params = cli_params(sys.argv[1:])
        
    except ValueError as e:
        print(f"参数格式错误：{e}", file=sys.stderr)
        sys.exit(1)
    result = request("/amazonAds/profiles", params, persist=True,
                     inline="--inline" in sys.argv[1:])
    if result.get("error"):
        sys.exit(1)

    if "profiles" in result:
        profiles = result.get("profiles", [])
        total = result.get("total", 0)
        refreshed = result.get("refreshed", False)
        hint = "(已穿透 /v2/profiles 刷新)" if refreshed else "(读自 DB 快照)"
        print(f"\n✓ 已找到 {total} 个 profile {hint}：", file=sys.stderr)
        for p in profiles:
            print(
                f"  - profileId={p.get('profileId')}  {p.get('accountInfoName', 'N/A')}  "
                f"{p.get('countryCode', '')} ({p.get('region', '')})  "
                f"currency={p.get('currencyCode', '')}",
                file=sys.stderr,
            )


if __name__ == "__main__":
    main()
