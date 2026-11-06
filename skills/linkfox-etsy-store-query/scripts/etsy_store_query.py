#!/usr/bin/env python3
"""Etsy 店铺查询：提供 JSON CLI、24 小时缓存与完整响应落盘。

用法：python etsy_store_query.py '<JSON 参数>' [--inline] [--no-cache]
支持网关根地址与路径配置，HTTP 和缓存统一交给公共调用器。
"""

import os

from call_api import run


API_PATH = "/ehunt/etsy/storeQuery"
SLUG = "linkfox-etsy-store-query"


def main(argv=None):
    previous_base = os.environ.get("LINKFOX_TOOL_GATEWAY")
    legacy_base = os.environ.get("LINKFOX_TOOL_GATEWAY_BASE")
    use_legacy_base = not previous_base and bool(legacy_base)
    if use_legacy_base:
        os.environ["LINKFOX_TOOL_GATEWAY"] = legacy_base
    path = os.environ.get("LINKFOX_EHUNT_STORE_QUERY_PATH") or API_PATH
    path = "/" + path.lstrip("/")
    try:
        run(path, SLUG, argv=argv)
    finally:
        if use_legacy_base:
            if previous_base is None:
                os.environ.pop("LINKFOX_TOOL_GATEWAY", None)
            else:
                os.environ["LINKFOX_TOOL_GATEWAY"] = previous_base


if __name__ == "__main__":
    main()
