#!/usr/bin/env python3
"""Etsy 类目检索：提供 JSON CLI、24 小时缓存和网关环境变量配置。

用法：python etsy_category_search.py '<JSON 参数>' [--inline] [--no-cache]
完整响应始终落盘；不超过 8 KB 时完整打印，否则输出摘要。
"""

from contextlib import contextmanager
import os
from pathlib import Path
import sys
from tempfile import NamedTemporaryFile

import call_api


API_PATH = "/ehunt/etsy/etsyCategorySearch"
SLUG = "linkfox-etsy-category-search"


@contextmanager
def _runtime_config():
    """按网关变量优先级配置请求，并将响应保存到当前目录。"""
    old_gateway = os.environ.get("LINKFOX_TOOL_GATEWAY")
    old_root = call_api._SESSION_CACHE.get("_root")
    legacy_gateway = os.environ.get("LINKFOX_TOOL_GATEWAY_BASE")
    try:
        if not old_gateway and legacy_gateway:
            os.environ["LINKFOX_TOOL_GATEWAY"] = legacy_gateway
        root = Path.cwd() / "linkfox"
        root.mkdir(parents=True, exist_ok=True)
        # 请求前验证写权限，避免公共调用器自动回退到家目录或临时目录。
        with NamedTemporaryFile(dir=root, prefix=".etsy-write-probe-"):
            pass
        call_api._SESSION_CACHE["_root"] = str(root)
        yield
    finally:
        if old_gateway is None:
            os.environ.pop("LINKFOX_TOOL_GATEWAY", None)
        else:
            os.environ["LINKFOX_TOOL_GATEWAY"] = old_gateway
        if old_root is None:
            call_api._SESSION_CACHE.pop("_root", None)
        else:
            call_api._SESSION_CACHE["_root"] = old_root


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        # 由公共入口处理缺少参数时的 usage 与退出码，不创建工作目录。
        return call_api.run(API_PATH, SLUG, argv=argv)
    configured_path = os.environ.get("LINKFOX_EHUNT_ETSY_CATEGORY_SEARCH_PATH")
    api_path = "/" + configured_path.lstrip("/") if configured_path else API_PATH
    try:
        with _runtime_config():
            # 由公共调用器统一管理缓存键、路径与 TTL，不叠加业务缓存。
            return call_api.run(api_path, SLUG, argv=argv)
    except OSError as exc:
        print(f"当前目录无法保存响应：{exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
