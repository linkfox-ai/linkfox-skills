#!/usr/bin/env python3
"""
Amazon Ads Profiles List - LinkFox Skill
Calls /amazonAds/profiles to list all profiles (DB snapshot; optionally refresh=true)

Usage:
  python profiles.py                          # read DB snapshot
  python profiles.py '{"refresh": true}'      # force upstream v2/profiles refresh
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

from _lf_output import emit_result, lf_inline_flag

# 生产默认走 tool-gateway.linkfox.com；开发/测试期可 export AMAZON_ADS_BASE_URL=<url> 覆盖
API_BASE_URL = (os.environ.get("LINKFOX_TOOL_GATEWAY") or os.environ.get("AMAZON_ADS_BASE_URL") or "https://tool-gateway.linkfox.com").rstrip("/")
API_ENDPOINT = f"{API_BASE_URL}/amazonAds/profiles"


def get_api_key():
    """
获取配置在环境变量的API Key。
如果获取不到，按 SKILL.md 的 **## 解决认证和积分问题** 处理。
"""
    key = os.environ.get("LINKFOX_AGENT_API_KEY") or os.environ.get("LINKFOXAGENT_API_KEY")
    if not key:
        print(
            "API Key 未配置",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


def call_api(params: dict) -> dict:
    api_key = get_api_key()
    data = json.dumps(params).encode("utf-8")
    req = Request(
        API_ENDPOINT,
        data=data,
        headers={
            "Authorization": api_key,
            "Content-Type": "application/json",
            "User-Agent": "LinkFox-Skill/1.0",
        },
        method="POST",
    )
    try:
        with urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        return {"error": f"HTTP {e.code}: {e.reason}", "details": body}
    except URLError as e:
        return {"error": f"Connection failed: {e.reason}"}


def main():
    params = {}
    if len(sys.argv) >= 2:
        try:
            params = json.loads(sys.argv[1])
        except json.JSONDecodeError as e:
            print(f"Invalid parameter format: {e}", file=sys.stderr)
            sys.exit(1)

    result = call_api(params)
    emit_result(result, lf_inline_flag())

    if "profiles" in result:
        profiles = result.get("profiles", [])
        total = result.get("total", 0)
        refreshed = result.get("refreshed", False)
        hint = "(已穿透 /v2/profiles 刷新)" if refreshed else "(读自 DB 快照)"
        print(f"\n✓ Found {total} profile(s) {hint}:", file=sys.stderr)
        for p in profiles:
            print(
                f"  - profileId={p.get('profileId')}  {p.get('accountInfoName', 'N/A')}  "
                f"{p.get('countryCode', '')} ({p.get('region', '')})  "
                f"currency={p.get('currencyCode', '')}",
                file=sys.stderr,
            )


if __name__ == "__main__":
    main()
