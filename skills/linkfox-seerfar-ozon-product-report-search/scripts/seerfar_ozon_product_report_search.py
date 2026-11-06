#!/usr/bin/env python3
"""Seerfar Ozon 商品报表搜索。

用法：
  python seerfar_ozon_product_report_search.py '<JSON 参数>' [--inline] [--no-cache]

缓存由公共调用器统一管理，有效期为 24 小时，业务封装不叠加缓存。
业务封装在请求前检查当前目录可写并固定输出根目录，避免回退到其他目录。
"""

import json
import os
import sys
import tempfile

import call_api
from call_api import run


API_PATH = "/seerfar/ozon/productReportSearch"
SLUG = "linkfox-seerfar-ozon-product-report-search"


def _with_http_status(transport, api_path, params):
    """保留公共调用器解析响应体时未返回的 HTTP 状态。"""
    previous_opener = call_api.urlopen
    status = None

    def capture_status(*args, **kwargs):
        nonlocal status
        try:
            response = previous_opener(*args, **kwargs)
        except call_api.HTTPError as exc:
            status = exc.code
            raise
        status = response.status
        return response

    call_api.urlopen = capture_status
    try:
        result = transport(api_path, params)
    finally:
        call_api.urlopen = previous_opener
    if isinstance(result, dict) and status is not None:
        result["_http_status"] = status
    return result


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    positional = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    # 无参数或 JSON 无效时，沿用公共调用器的 CLI 错误，不创建输出目录。
    try:
        if not positional:
            return run(API_PATH, SLUG, argv=argv)
        json.loads(positional[0])
    except json.JSONDecodeError:
        return run(API_PATH, SLUG, argv=argv)

    root = os.path.abspath(os.path.join(os.getcwd(), "linkfox"))
    previous_root = call_api._SESSION_CACHE.get("_root")
    call_api._SESSION_CACHE["_root"] = root
    try:
        try:
            # 预先建立会话及数据目录；不可写时在收费请求前退出。
            _, session_dir = call_api._ensure_session(int(call_api.time.time()))
            data_dir = os.path.join(session_dir, "data")
            os.makedirs(data_dir, exist_ok=True)
            with tempfile.TemporaryFile(dir=data_dir):
                pass
            with open(os.path.join(session_dir, "_meta.json"), "a", encoding="utf-8"):
                pass
        except OSError as exc:
            print(f"当前目录无法保存完整响应：{exc}", file=sys.stderr)
            raise SystemExit(1)
        previous_transport = call_api.call_api
        call_api.call_api = lambda path, params: _with_http_status(previous_transport, path, params)
        try:
            return run(API_PATH, SLUG, argv=argv)
        finally:
            call_api.call_api = previous_transport
    finally:
        if previous_root is None:
            call_api._SESSION_CACHE.pop("_root", None)
        else:
            call_api._SESSION_CACHE["_root"] = previous_root


if __name__ == "__main__":
    main()
