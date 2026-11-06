#!/usr/bin/env python3
"""storeTokens 辅助函数的命令行入口；不执行授权。"""
import json
import sys
from _shopee_global_product_common import (
    ensure_auth_skill_available, resolve_store_tokens, emit_result, lf_inline_flag,
)


def main():
    if "--help" in sys.argv[1:] or "-h" in sys.argv[1:]:
        print("用法: store_tokens.py '<JSON>' [--inline] [--no-cache]")
        return
    if len(sys.argv) < 2:
        print("缺少 JSON 参数", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    if not params.get("skipDepCheck"):
        ensure_auth_skill_available("store_tokens.py")
    emit_result(resolve_store_tokens(params), slug="linkfox-shopee-store-global-product-storeTokens", inline=lf_inline_flag())


if __name__ == "__main__":
    main()
