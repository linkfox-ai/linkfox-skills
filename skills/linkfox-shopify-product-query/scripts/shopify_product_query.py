#!/usr/bin/env python3
"""Shopify 商品查询：复用公共调用器的请求、24 小时缓存与输出流程。

用法：python shopify_product_query.py '<JSON 参数>' [--inline] [--no-cache]
支持通过环境变量配置网关根地址与路径，完整数据只保存到当前工作目录；不可写时在请求前报错。
"""

import json
import os
from pathlib import Path
import sys
import tempfile
import time

import call_api


API_PATH = "/ehunt/shopify/productQuery"
SLUG = "linkfox-shopify-product-query"


def get_api_base():
    return (os.environ.get("LINKFOX_TOOL_GATEWAY")
            or os.environ.get("LINKFOX_TOOL_GATEWAY_BASE")
            or "https://tool-gateway.linkfox.com").rstrip("/")


def get_api_path():
    path = os.environ.get("LINKFOX_EHUNT_SHOPIFY_PRODUCT_QUERY_PATH") or API_PATH
    return "/" + path.lstrip("/")


def _request_with_http_status(request, api_path, params):
    """保留实际 HTTP 状态，不改变公共调用器对响应体的解析。"""
    status = None
    original_urlopen = call_api.urlopen

    def capture_status(*args, **kwargs):
        nonlocal status
        try:
            response = original_urlopen(*args, **kwargs)
        except call_api.HTTPError as error:
            status = error.code
            raise
        status = response.status
        return response

    call_api.urlopen = capture_status
    try:
        result = request(api_path, params)
    finally:
        call_api.urlopen = original_urlopen
    if isinstance(result, dict) and status is not None:
        result["_http_status"] = status
    return result


def _prepare_output():
    cwd = Path.cwd().resolve()
    if os.name != "nt" and (cwd == Path("/tmp") or Path("/tmp") in cwd.parents):
        raise OSError("按本技能约定，不得将会话数据写入 /tmp")
    root = cwd / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    # 业务入口将会话数据限定在当前工作目录。
    call_api._SESSION_CACHE["_root"] = str(root)
    # 根目录可写不代表完整会话路径可写（例如 Windows 长路径限制）。
    # 提前创建同一会话目录，并用等长文件名检查实际数据文件能否落盘。
    _, session_dir = call_api._ensure_session(time.time())
    data_dir = Path(session_dir) / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=data_dir, prefix=SLUG + "-" + "0" * 8,
                                suffix=".json"):
        pass


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    values = [value for value in args if value not in ("--inline", "--no-cache")]
    # 空参数和非法 JSON 交由公共 CLI 报错，不做任何网络请求。
    if values:
        try:
            json.loads(values[0])
        except json.JSONDecodeError:
            return call_api.run(get_api_path(), SLUG, argv=args)
        try:
            _prepare_output()
        except OSError as error:
            print(f"当前工作目录不可用于保存响应：{error}", file=sys.stderr)
            raise SystemExit(1)

    original_base = os.environ.get("LINKFOX_TOOL_GATEWAY")
    os.environ["LINKFOX_TOOL_GATEWAY"] = get_api_base()
    original_request = call_api.call_api

    def request_with_status(api_path, params):
        return _request_with_http_status(original_request, api_path, params)

    call_api.call_api = request_with_status
    try:
        # 由公共调用器负责缓存读写，--no-cache 原样传递。
        return call_api.run(get_api_path(), SLUG, argv=args)
    finally:
        call_api.call_api = original_request
        if original_base is None:
            os.environ.pop("LINKFOX_TOOL_GATEWAY", None)
        else:
            os.environ["LINKFOX_TOOL_GATEWAY"] = original_base


if __name__ == "__main__":
    main()
