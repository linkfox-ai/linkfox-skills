#!/usr/bin/env python3
"""
Amazon Ads Token Refresh - LinkFox Skill
Calls /amazonAds/refreshToken to refresh access token

Usage:
  python refresh_token.py '{"authRecordId": 123}'
  python refresh_token.py '{"profileId": 1234567890}'
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

from _lf_output import emit_result, lf_inline_flag

# 生产默认走 tool-gateway.linkfox.com；开发/测试期可 export AMAZON_ADS_BASE_URL=<url> 覆盖
API_BASE_URL = (os.environ.get("LINKFOX_TOOL_GATEWAY") or os.environ.get("AMAZON_ADS_BASE_URL") or "https://tool-gateway.linkfox.com").rstrip("/")
API_ENDPOINT = f"{API_BASE_URL}/amazonAds/refreshToken"


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
    if len(sys.argv) < 2:
        print("Usage: refresh_token.py '<JSON parameters>'", file=sys.stderr)
        print("Required: authRecordId OR profileId", file=sys.stderr)
        sys.exit(1)

    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid parameter format: {e}", file=sys.stderr)
        sys.exit(1)

    if "authRecordId" not in params and "profileId" not in params:
        print("Error: 'authRecordId' or 'profileId' is required (choose one)", file=sys.stderr)
        sys.exit(1)

    result = call_api(params)

    def _mask_token(t):
        if not isinstance(t, str) or len(t) < 20:
            return "***"
        return t[:8] + "..." + t[-4:]

    if "accessToken" in result:
        result["accessToken"] = _mask_token(result["accessToken"])
    if "refreshToken" in result:
        result["refreshToken"] = _mask_token(result["refreshToken"])

    emit_result(result, lf_inline_flag())

    if "message" in result:
        print(f"\n✓ {result['message']}", file=sys.stderr)
        print("Note: Tokens have been masked for security. Full tokens are stored in database.", file=sys.stderr)


if __name__ == "__main__":
    main()
