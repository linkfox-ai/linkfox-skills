#!/usr/bin/env python3
"""Etsy 商品查询：读取网关配置，复用公共缓存、落盘和输出流程。

用法：
  python etsy_product_query.py '<JSON 参数>' [--inline] [--no-cache]

公共调用器是唯一响应缓存层，使用基于查询参数哈希的缓存文件和 24 小时有效期。
业务封装负责兼容配置、落实当前工作目录的落盘要求，并避免连续查询覆盖响应文件。
"""

import json
import os
from pathlib import Path
import sys
import tempfile
import time

import call_api


API_PATH = "/ehunt/etsy/productQuery"
SLUG = "linkfox-etsy-product-query"


def get_api_base():
    """优先读取 LINKFOX_TOOL_GATEWAY，其次读取 LINKFOX_TOOL_GATEWAY_BASE。"""
    return (
        os.environ.get("LINKFOX_TOOL_GATEWAY")
        or os.environ.get("LINKFOX_TOOL_GATEWAY_BASE")
        or "https://tool-gateway.linkfox.com"
    ).rstrip("/")


def get_api_path():
    configured = os.environ.get("LINKFOX_EHUNT_PRODUCT_QUERY_PATH") or API_PATH
    return "/" + configured.lstrip("/")


def _prepare_output_root():
    """在付费请求前检查会话目录，不回退到家目录或临时目录。"""
    cwd = Path.cwd().resolve()
    if cwd == Path("/tmp").resolve() or Path("/tmp").resolve() in cwd.parents:
        raise OSError("当前工作目录不能位于 /tmp，请先切换到可写的项目目录")
    root = cwd / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    call_api._SESSION_CACHE["_root"] = str(root)
    _, session_dir = call_api._ensure_session(time.time())
    data_dir = Path(session_dir) / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=data_dir) as probe:
        probe.write(b"linkfox-output-check")
    return root


def _resolve_output_path(slug, ts):
    """为每份完整响应预留独立文件，避免公共流程的秒级时间戳覆盖前次结果。"""
    precise_ts = max(time.time(), ts)
    while True:
        path = call_api.resolve_data_path(slug, precise_ts)
        try:
            with open(path, "x", encoding="utf-8"):
                pass
        except FileExistsError:
            precise_ts += 0.000001
        else:
            return path


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--help" in argv or "-h" in argv:
        print("用法：etsy_product_query.py '<JSON 参数>' [--inline] [--no-cache]")
        print("默认使用 24 小时本地缓存；--no-cache 禁用缓存，--inline 全量输出。")
        return

    # 无参数或 JSON 格式错误由公共调用器输出 CLI 诊断，且不会发请求。
    positional = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    if not positional:
        return call_api.run(get_api_path(), SLUG, argv=argv)
    try:
        json.loads(positional[0])
    except json.JSONDecodeError:
        return call_api.run(get_api_path(), SLUG, argv=argv)

    old_gateway = os.environ.get("LINKFOX_TOOL_GATEWAY")
    old_root = call_api._SESSION_CACHE.get("_root")
    old_output_resolver = call_api._resolve_output_path
    try:
        os.environ["LINKFOX_TOOL_GATEWAY"] = get_api_base()
        try:
            _prepare_output_root()
        except OSError as exc:
            raise SystemExit(f"当前目录无法保存完整响应：{exc}") from exc
        call_api._resolve_output_path = _resolve_output_path
        # run 提供唯一响应缓存层。
        return call_api.run(get_api_path(), SLUG, argv=argv)
    finally:
        call_api._resolve_output_path = old_output_resolver
        if old_gateway is None:
            os.environ.pop("LINKFOX_TOOL_GATEWAY", None)
        else:
            os.environ["LINKFOX_TOOL_GATEWAY"] = old_gateway
        if old_root is None:
            call_api._SESSION_CACHE.pop("_root", None)
        else:
            call_api._SESSION_CACHE["_root"] = old_root


if __name__ == "__main__":
    main()
