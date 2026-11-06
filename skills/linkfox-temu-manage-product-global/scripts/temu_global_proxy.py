#!/usr/bin/env python3
"""
Temu 全球区商品管理通用转发入口（默认全球区半托管）。

Usage:
  python temu_global_proxy.py '{
    "accessToken": "TEMU_GLOBAL_TOKEN",
    "type": "bg.local.goods.list.query",
    "params": {"request": {"pageNo": 1, "pageSize": 20, "goodsSearchType": 1, "goodsStatusFilterType": 0}}
  }'
"""

import json
import sys

from _temu_common import emit_result, lf_inline_flag, load_json_arg, parse_nested_body, require_text
from _temu_global_common import DEFAULT_SITE, global_proxy_call

def main():
    if len(sys.argv) < 2:
        print("Usage: temu_global_proxy.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = load_json_arg(sys.argv)
    params.setdefault("site", DEFAULT_SITE)
    api_type = require_text(params, "type")
    result = parse_nested_body(global_proxy_call(params, api_type))
    emit_result(result, inline=lf_inline_flag())

if __name__ == "__main__":
    main()
