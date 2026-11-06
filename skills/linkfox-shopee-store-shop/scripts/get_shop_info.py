#!/usr/bin/env python3
"""
Shopee Store — get_shop_info

官方: https://open.shopee.com/documents/v2/v2.shop.get_shop_info?module=92&type=1

入参说明见 references/apis/get-shop-info.md。
"""

from __future__ import annotations

import json
import sys

from _shop_api_runner import emit_result, lf_inline_flag, run_shop_api


def main() -> None:
    if "--help" in sys.argv[1:] or "-h" in sys.argv[1:]:
        print(__doc__)
        print("选项：--inline 完整打印；--no-cache（本技能始终禁用响应缓存）")
        return
    if len(sys.argv) < 2:
        print("Usage: get_shop_info.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    try:
        params = json.loads(sys.argv[1])
        if not isinstance(params, dict):
            raise ValueError("JSON 参数必须为对象")
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"参数错误：{exc}", file=sys.stderr)
        sys.exit(1)
    result = run_shop_api("get_shop_info", params, "get_shop_info.py")
    inline = lf_inline_flag()
    emit_result(result, inline=inline)


if __name__ == "__main__":
    main()
