#!/usr/bin/env python3
"""
Amazon Opportunity Screener by Metrics - LinkFox Skill
反向选品：基于历史商业洞察报告沉淀的指标数据池，按 30+ 项商业维度反查亚马逊赛道与关键词。
Calls the amazon/opportunity/searchByMetrics API endpoint.

Usage:
  python amazon_opportunity_screener.py '<JSON parameters>'

Examples:
  python amazon_opportunity_screener.py '{"keyword": "whoop band", "limit": 25}'
  python amazon_opportunity_screener.py '{"nicheBrandCountLte": 20, "nicheSearchVolumeYoyChangePctAtLeastGte": 100}'
"""

import json
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


API_URL = "https://tool-gateway.linkfox.com/amazon/opportunity/searchByMetrics"


def get_api_key():
    """从环境变量读取 API Key，缺失时友好提示。"""
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
    """调用工具网关 API。"""
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
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        return {"error": f"HTTP {e.code}: {e.reason}", "details": body}
    except URLError as e:
        return {"error": f"Connection failed: {e.reason}"}


def main():
    if len(sys.argv) < 2:
        print("Usage: amazon_opportunity_screener.py '<JSON parameters>'", file=sys.stderr)
        print(
            'Example: amazon_opportunity_screener.py \'{"keyword": "whoop band", "limit": 25}\'',
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
