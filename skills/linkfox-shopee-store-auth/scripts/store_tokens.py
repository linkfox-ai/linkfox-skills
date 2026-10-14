#!/usr/bin/env python3
"""
Shopee Store Tokens Query - LinkFox Skill
Calls /shopee/storeTokens to get authorization status for a store + appType

Usage:
  python store_tokens.py '{"shopId": "67890", "appType": "erp"}'
  python store_tokens.py '{"shopId": "67890", "appType": "ad"}'
  python store_tokens.py '{"merchantId": "12345"}'
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

from _lf_output import emit_result, lf_inline_flag
from _token_status_output import strip_raw_tokens, print_status_note

# 生产默认走 tool-gateway.linkfox.com；开发/测试期可 export SHOPEE_API_BASE_URL=<url> 覆盖
API_BASE_URL = (os.environ.get("LINKFOX_TOOL_GATEWAY") or os.environ.get("SHOPEE_API_BASE_URL") or "https://tool-gateway.linkfox.com").rstrip("/")
API_ENDPOINT = f"{API_BASE_URL}/shopee/storeTokens"


def get_api_key():
    """
    获取配置在环境变量的API Key。
    如果获取不到，按 SKILL.md 的 **## 解决认证和算力问题** 处理。
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
            "User-Agent": "LinkFox-Skill/2.0",
        },
        method="POST",
    )
    try:
        with urlopen(req, timeout=150) as response:
            result = json.loads(response.read().decode("utf-8"))
            error_code = str(result.get("errcode", ""))
            if error_code.isdigit() and int(error_code) not in (0, 200):
                raise SystemExit(json.dumps(result, ensure_ascii=False))
            return result
    except HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        return {"error": f"HTTP {e.code}: {e.reason}", "details": body}
    except URLError as e:
        return {"error": f"Connection failed: {e.reason}"}


def main():
    if len(sys.argv) < 2:
        print("Usage: store_tokens.py '<JSON parameters>'", file=sys.stderr)
        print("Required: shopId OR merchantId; optional appType=erp|ad (default erp)", file=sys.stderr)
        sys.exit(1)

    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid parameter format: {e}", file=sys.stderr)
        sys.exit(1)

    if "shopId" not in params and "merchantId" not in params:
        print("Error: 'shopId' or 'merchantId' is required (choose one)", file=sys.stderr)
        sys.exit(1)

    raw_app = params.get("appType")
    if raw_app is None or (isinstance(raw_app, str) and not str(raw_app).strip()):
        params["appType"] = "erp"
    else:
        app_type = str(raw_app).strip().lower()
        if app_type not in ("erp", "ad"):
            print(
                f"Error: 'appType' must be 'erp' or 'ad', got {raw_app!r}",
                file=sys.stderr,
            )
            sys.exit(1)
        params["appType"] = app_type

    result = call_api(params)
    result = strip_raw_tokens(result)
    emit_result(result, lf_inline_flag())
    print_status_note(result)


if __name__ == "__main__":
    main()
