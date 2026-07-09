#!/usr/bin/env python3
"""
西柚找词 (Xiyou) — LinkFox Skill
Calls LinkFox gateway /xiyou/* endpoints (proxied to Xiyou OpenAPI).

Usage:
  python xiyou.py --list-apis
  python xiyou.py --api asinTraffic --params '{"entities":[{"country":"US","asin":"B06XZTZ7GB"}]}'
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _xiyou_common import call_xiyou_api, emit_result, lf_inline_flag  # noqa: E402

APIS: dict[str, str] = {
    "asinTraffic": "ASIN 流量得分",
    "asinInfo": "ASIN 商品信息",
    "asinInfoChangeTrend": "ASIN 基础信息变动趋势（天）",
    "asinTrafficScoreTrend": "ASIN 流量得分趋势（天）",
    "asinAdvertisingChangeTrend": "ASIN 广告信息变动趋势（天）",
    "asinBsrTrend": "ASIN BSR 排名趋势（天）",
    "asinOrdersTrend": "ASIN 订单量趋势（月）",
    "asinInfoDailyTrend": "ASIN 商品信息趋势（天）",
    "asinResearchPeriod": "ASIN 反查关键词（最近天）",
    "asinResearchMonthly": "ASIN 反查关键词（月）",
    "asinVariations": "获取 ASIN 变体",
    "asinSearchTermTrafficTrend": "ASIN 词流量趋势（天）",
    "asinSearchTermRankTrendDaily": "ASIN 词排名趋势（天）",
    "asinSearchTermRankTrendHourly": "ASIN 词排名趋势（小时）",
    "searchTermAnalysisPeriod": "关键词分析列表（最近天）",
    "searchTermAbaWeeklyTrend": "关键词 ABA 数据趋势（周）",
    "searchTermInfo": "关键词信息（最近一周）",
}


def print_api_list() -> None:
    print("Available --api values:\n")
    for idx, (name, title) in enumerate(APIS.items(), start=1):
        print(f"  {idx:2}. {name:<32} {title}")
    print("\nSee references/api.md for request parameters per API.")


def parse_args() -> tuple[str, dict]:
    if len(sys.argv) >= 2 and sys.argv[1].startswith("{"):
        try:
            payload = json.loads(sys.argv[1])
        except json.JSONDecodeError as exc:
            print(f"Invalid JSON parameters: {exc}", file=sys.stderr)
            sys.exit(1)
        if not isinstance(payload, dict):
            print("Parameters must be a JSON object", file=sys.stderr)
            sys.exit(1)
        route = payload.get("api")
        if not route:
            print('JSON parameters must include "api" field', file=sys.stderr)
            sys.exit(1)
        params = {k: v for k, v in payload.items() if k != "api"}
        return str(route), params

    parser = argparse.ArgumentParser(description="Xiyou (西柚找词) gateway client")
    parser.add_argument("--api", help="API route name (e.g. asinTraffic)")
    parser.add_argument(
        "--params",
        default="{}",
        help='JSON object for request body (clientId/clientSecret auto-injected)',
    )
    parser.add_argument("--list-apis", action="store_true", help="List supported APIs")
    args = parser.parse_args()

    if args.list_apis:
        print_api_list()
        sys.exit(0)

    if not args.api:
        parser.print_help(file=sys.stderr)
        sys.exit(1)

    try:
        params = json.loads(args.params)
    except json.JSONDecodeError as exc:
        print(f"Invalid --params JSON: {exc}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(params, dict):
        print("--params must be a JSON object", file=sys.stderr)
        sys.exit(1)

    return args.api.strip(), params


def main() -> None:
    if len(sys.argv) == 2 and sys.argv[1] in ("--list-apis", "-h", "--help"):
        if sys.argv[1] == "--list-apis":
            print_api_list()
        else:
            argparse.ArgumentParser(description="Xiyou (西柚找词) gateway client").print_help()
        return

    route, params = parse_args()
    if route not in APIS:
        print(f"Unknown API: {route}", file=sys.stderr)
        print_api_list()
        sys.exit(1)

    result = call_xiyou_api(route, params)
    inline = lf_inline_flag()
    emit_result(result, inline)


if __name__ == "__main__":
    main()
