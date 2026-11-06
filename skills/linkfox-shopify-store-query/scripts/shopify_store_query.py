#!/usr/bin/env python3
"""Shopify 店铺查询：支持 JSON CLI、24 小时缓存和会话输出。

用法：python shopify_store_query.py '<JSON 参数>' [--inline] [--no-cache]
认证、请求、缓存和完整响应落盘统一使用公共调用器。
"""

import os
import sys
import tempfile
import time
from pathlib import Path
from urllib.error import HTTPError

import call_api as api
from call_api import run


API_PATH = "/ehunt/shopify/storeQuery"
SLUG = "linkfox-shopify-store-query"


def _call_with_http_status(call, api_path, params):
    """沿用公共请求与错误解析，同时保留本次 HTTP 状态用于失败判断。"""
    old_urlopen = api.urlopen
    http_status = None

    def capture_status(*args, **kwargs):
        nonlocal http_status
        try:
            response = old_urlopen(*args, **kwargs)
        except HTTPError as exc:
            http_status = exc.code
            raise
        http_status = response.status
        return response

    api.urlopen = capture_status
    try:
        result = call(api_path, params)
    finally:
        api.urlopen = old_urlopen
    if isinstance(result, dict) and http_status is not None:
        result["_http_status"] = http_status
    return result


def _prepare_output_root():
    """请求前验证当前目录，落实禁止回退到其他目录的输出约定。"""
    cwd = Path.cwd().resolve()
    forbidden = Path("/tmp").resolve()
    if cwd == forbidden or forbidden in cwd.parents:
        raise SystemExit("请从可写的任务目录运行，本技能禁止将响应写入 /tmp。")
    root = cwd / "linkfox"
    try:
        root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryFile(dir=root):
            pass
    except OSError as exc:
        raise SystemExit(f"当前目录不可写，未发起查询：{exc}") from exc
    return str(root)


def main(argv=None):
    """支持网关根地址和接口路径覆盖；缓存由公共调用器统一处理。"""
    argv = list(sys.argv[1:] if argv is None else argv)
    api_path = os.environ.get("LINKFOX_EHUNT_SHOPIFY_STORE_QUERY_PATH") or API_PATH
    api_path = "/" + api_path.lstrip("/")
    old_base = os.environ.get("LINKFOX_TOOL_GATEWAY")
    legacy_base = os.environ.get("LINKFOX_TOOL_GATEWAY_BASE")
    use_legacy = not old_base and bool(legacy_base)
    old_root = api._SESSION_CACHE.get("_root")
    old_output_path = api._resolve_output_path
    old_call_api = api.call_api
    # 无参数时由公共调用器报告 CLI 用法，不创建输出目录。
    if any(arg not in ("--inline", "--no-cache") for arg in argv):
        api._SESSION_CACHE["_root"] = _prepare_output_root()
    # 公共调用器使用整秒时间；保留同一秒内的每份响应，避免覆盖。
    api._resolve_output_path = lambda slug, _ts: api.resolve_data_path(slug, time.time())
    if use_legacy:
        os.environ["LINKFOX_TOOL_GATEWAY"] = legacy_base
    try:
        api.call_api = lambda path, params: _call_with_http_status(old_call_api, path, params)
        run(api_path, SLUG, argv=argv)
    finally:
        api.call_api = old_call_api
        api._resolve_output_path = old_output_path
        if old_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = old_root
        if use_legacy:
            if old_base is None:
                os.environ.pop("LINKFOX_TOOL_GATEWAY", None)
            else:
                os.environ["LINKFOX_TOOL_GATEWAY"] = old_base


if __name__ == "__main__":
    main()
