#!/usr/bin/env python3
"""Temu 店铺查询：提供 CLI、单层缓存和网关环境配置，经公共 run 调用。"""

from contextlib import contextmanager
import os
from pathlib import Path
import sys
import tempfile
import time
from urllib.error import HTTPError

import call_api


API_PATH = "/ehunt/temu/storeQuery"
SLUG = "linkfox-temu-store-query"


def get_api_base():
    """主网关变量优先，兼容 LINKFOX_TOOL_GATEWAY_BASE 别名。"""
    return (os.environ.get("LINKFOX_TOOL_GATEWAY")
            or os.environ.get("LINKFOX_TOOL_GATEWAY_BASE")
            or "https://tool-gateway.linkfox.com").rstrip("/")


def get_api_path():
    path = os.environ.get("LINKFOX_EHUNT_TEMU_STORE_QUERY_PATH") or API_PATH
    return "/" + path.lstrip("/")


@contextmanager
def _http_diagnostics():
    """复用公共请求和错误解析，仅为对象响应保留实际 HTTP 状态。"""
    previous_call = call_api.call_api
    previous_open = call_api.urlopen

    def call_with_status(api_path, params):
        status = None

        def open_with_status(*args, **kwargs):
            nonlocal status
            try:
                response = previous_open(*args, **kwargs)
            except HTTPError as exc:
                status = exc.code
                raise
            status = response.status
            return response

        call_api.urlopen = open_with_status
        try:
            result = previous_call(api_path, params)
        finally:
            call_api.urlopen = previous_open
        if isinstance(result, dict) and status is not None:
            result["_http_status"] = status
        return result

    call_api.call_api = call_with_status
    try:
        yield
    finally:
        call_api.call_api = previous_call


@contextmanager
def _runtime():
    """在业务封装内落实当前目录输出约定，不改公共资源或增加缓存。"""
    cwd = Path.cwd().resolve()
    root = (cwd / "linkfox").resolve()
    try:
        root.relative_to(cwd)
    except ValueError as exc:
        raise OSError("linkfox 输出根目录超出当前工作目录") from exc
    if os.name != "nt" and (root == Path("/tmp") or Path("/tmp") in root.parents):
        raise OSError("会话数据禁止写入 /tmp，请切换到可写的工作目录")
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass

    # 在收费请求前检查实际会话目录，而不只检查 linkfox 根目录。
    ts = time.time()
    date_dir = (root / time.strftime("%Y-%m-%d", time.localtime(ts))).resolve()
    session_dir = (date_dir / call_api._session_id(ts)).resolve()
    data_dir = (session_dir / "data").resolve()
    try:
        date_dir.relative_to(root)
        session_dir.relative_to(date_dir)
        data_dir.relative_to(session_dir)
        if session_dir == date_dir:
            raise ValueError("会话标识为空目录")
    except ValueError as exc:
        raise OSError("SESSION_ID 或会话目录超出当前工作目录的输出范围") from exc
    data_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=data_dir):
        pass

    previous_base = os.environ.get("LINKFOX_TOOL_GATEWAY")
    previous_root = call_api._SESSION_CACHE.get("_root")
    os.environ["LINKFOX_TOOL_GATEWAY"] = get_api_base()
    call_api._SESSION_CACHE["_root"] = str(root)
    try:
        call_api._ensure_session(ts)
        yield
    finally:
        if previous_base is None:
            os.environ.pop("LINKFOX_TOOL_GATEWAY", None)
        else:
            os.environ["LINKFOX_TOOL_GATEWAY"] = previous_base
        if previous_root is None:
            call_api._SESSION_CACHE.pop("_root", None)
        else:
            call_api._SESSION_CACHE["_root"] = previous_root


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv in (["--help"], ["-h"]):
        print("用法：python scripts/temu_store_query.py '<JSON 参数>' [--inline] [--no-cache]")
        print("默认复用 24 小时本地缓存；--inline 全量输出；--no-cache 跳过缓存读写。")
        return 0
    if not argv:
        return call_api.run(get_api_path(), SLUG, argv=argv)
    try:
        with _runtime(), _http_diagnostics():
            call_api.run(get_api_path(), SLUG, argv=argv)
    except OSError as exc:
        print(f"当前工作目录不可写或数据保存失败：{exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
