#!/usr/bin/env python3
"""
Shopee Store — create_publish_task

官方: https://open.shopee.com/documents/v2/v2.global_product.create_publish_task?module=90&type=1

入参说明见 references/apis/create-publish-task.md。
"""

from __future__ import annotations

import json
import sys

from _global_product_api_runner import run_global_product_api
from _shopee_global_product_common import emit_result, lf_inline_flag


def main() -> None:
    if "--help" in sys.argv[1:] or "-h" in sys.argv[1:]:
        print("用法: create_publish_task.py '<JSON>' [--inline] [--no-cache]")
        return
    if len(sys.argv) < 2:
        print("Usage: create_publish_task.py '<JSON>'", file=sys.stderr)
        sys.exit(1)
    params = json.loads(sys.argv[1])
    emit_result(run_global_product_api("create_publish_task", params, "create_publish_task.py"), slug="linkfox-shopee-store-global-product-create_publish_task", inline=lf_inline_flag())


if __name__ == "__main__":
    main()
