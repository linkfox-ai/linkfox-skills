#!/usr/bin/env python3
"""
Amazon Policy & Regulation Feed (list) - LinkFox Skill
调用 amazon/policyFeed 接口，按站点 / 时间区间分页查询
亚马逊最新政策法规与资讯列表（含 AI 中文摘要）。

Usage:
  python amazon_policy_feed.py '{"site": "US", "pageSize": 20}'
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


API_URL = "https://tool-gateway.linkfox.com/amazon/policyFeed"


def get_api_key():
    key = os.environ.get("LINKFOXAGENT_API_KEY")
    if not key:
        print(
            "API Key not configured. Please complete authorization first:\n"
            "1. Visit https://skill.linkfox.com/linkfoxskills/guide.htm to obtain your Key\n"
            "2. Set the environment variable: export LINKFOXAGENT_API_KEY=your-key-here",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


def call_api(params: dict) -> dict:
    api_key = get_api_key()
    data = json.dumps(params).encode("utf-8")

    req = Request(
        API_URL,
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
            result = json.loads(response.read().decode("utf-8"))
        if isinstance(result, dict) and "errcode" in result and result["errcode"] != 200:
            print(
                f"Business error: errcode={result['errcode']}, errmsg={result.get('errmsg', '')}",
                file=sys.stderr,
            )
        return result
    except HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        try:
            parsed = json.loads(body) if body else None
        except (json.JSONDecodeError, ValueError):
            parsed = None
        if isinstance(parsed, dict) and "code" in parsed:
            return parsed
        errmsg = f"HTTP {e.code}: {e.reason}"
        if body:
            errmsg += f" - {body}"
        return {"code": str(e.code), "msg": errmsg}
    except URLError as e:
        return {"code": "-1", "msg": f"Connection failed: {e.reason}"}

def main():
    if len(sys.argv) < 2:
        print("Usage: amazon_policy_feed.py '<JSON parameters>'", file=sys.stderr)
        print(
            'Example: amazon_policy_feed.py \'{"site": "US", "pageSize": 20}\'',
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid parameter format: {e}", file=sys.stderr)
        sys.exit(1)

    result = call_api(params)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
