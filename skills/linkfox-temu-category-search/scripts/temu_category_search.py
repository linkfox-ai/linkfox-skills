#!/usr/bin/env python3
"""Temu 类目检索与同步 CLI，使用 24 小时缓存和可配置的网关。"""

import hashlib
import json
import os
import sys
import time
from contextlib import contextmanager

import call_api as gateway


API_PATH = "/ehunt/temu/temuCategorySearch"
SYNC_PATH = "/ehunt/temu/syncTemuCategory"
SLUG = "linkfox-temu-category-search"
CACHE_TTL_SEC = 24 * 60 * 60


def get_api_base():
    return (os.environ.get("LINKFOX_TOOL_GATEWAY")
            or os.environ.get("LINKFOX_TOOL_GATEWAY_BASE")
            or "https://tool-gateway.linkfox.com").rstrip("/")


def get_api_path():
    path = os.environ.get("LINKFOX_EHUNT_TEMU_CATEGORY_SEARCH_PATH") or API_PATH
    return "/" + path.lstrip("/")


def get_api_url():
    return get_api_base() + get_api_path()


def _cache_key(params):
    raw = json.dumps(params, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _cache_path(params):
    cwd = os.getcwd()
    path = os.path.join(cwd, "linkfox", ".cache", SLUG)
    os.makedirs(path, exist_ok=True)
    return os.path.join(path, f"{SLUG}-{_cache_key(params)}.json")


def _load_cache(path):
    if not os.path.isfile(path):
        return None
    if time.time() - os.path.getmtime(path) > CACHE_TTL_SEC:
        return None
    try:
        with open(path, encoding="utf-8") as f:
            payload = json.load(f)
        if isinstance(payload, dict):
            payload.setdefault("_cache", {})["hit"] = True
            payload.setdefault("_http_status", None)
            _report_http_status(payload["_http_status"], cached=True)
        return payload
    except (OSError, json.JSONDecodeError):
        return None


def _save_cache(path, payload):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def _report_http_status(status, *, cached=False):
    source = "缓存记录的 HTTP 状态" if cached else "HTTP 状态"
    print(f"{source}: {status if status is not None else '未知（未记录状态或连接失败）'}",
          file=sys.stderr)


@contextmanager
def _legacy_runtime():
    """在本次 run 内使用原始 JSON 缓存，结束时还原公共模块的运行时绑定。

    公共 run 自带缓存编排，适配其读写函数即可维持一层缓存；不修改公共文件。
    同时支持备用基础地址覆盖变量。
    """
    original_call_api = gateway.call_api

    def call_with_status(api_path, params):
        status, payload = original_call_api(api_path, params)
        _report_http_status(status)
        if isinstance(payload, dict):
            payload = dict(payload)
            payload["_http_status"] = status
        return status, payload

    replacements = {
        "call_api": call_with_status,
        "get_api_base": get_api_base,
        "_load_cache": _load_cache,
        "_save_cache": lambda path, payload, http_status: _save_cache(path, payload),
    }
    previous = {name: getattr(gateway, name) for name in replacements}
    try:
        for name, value in replacements.items():
            setattr(gateway, name, value)
        yield
    finally:
        for name, value in previous.items():
            setattr(gateway, name, value)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--help" in argv or "-h" in argv:
        print("用法: temu_category_search.py '<JSON 参数>' [--inline] [--no-cache] [--sync]")
        print("检索默认使用 24 小时缓存；--sync 使用 {} 同步类目树，始终跳过缓存。")
        return

    sync = "--sync" in argv
    argv = [value for value in argv if value != "--sync"]
    params_argv = [value for value in argv if value not in ("--inline", "--no-cache")]
    if sync and params_argv:
        try:
            params = json.loads(params_argv[0])
        except json.JSONDecodeError as exc:
            print(f"JSON 参数格式无效: {exc}", file=sys.stderr)
            raise SystemExit(1)
        if params != {}:
            print("类目同步无业务入参，请传入空对象 {}。", file=sys.stderr)
            raise SystemExit(1)
    path = SYNC_PATH if sync else get_api_path()
    slug = SLUG + "-sync" if sync else SLUG
    if sync and "--no-cache" not in argv:
        argv.append("--no-cache")
    # 无参数时维持公共 CLI 的非零退出与用法提示，避免将 flag 当 JSON。
    if not params_argv:
        argv = []
    with _legacy_runtime():
        gateway.run(path, slug, argv=argv)


if __name__ == "__main__":
    main()
