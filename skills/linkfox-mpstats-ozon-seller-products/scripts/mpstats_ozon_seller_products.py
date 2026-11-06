#!/usr/bin/env python3
"""MPSTATS Ozon 卖家商品查询。

用法：python mpstats_ozon_seller_products.py '<JSON 参数>' [--inline] [--no-cache]
公共调用器提供单层 24 小时缓存、认证、摘要和会话数据登记。
业务入口保证完整响应只落在当前工作目录，目录不可写时在请求前报错。
"""

import os
import sys
import tempfile
import time
from urllib.error import HTTPError

import call_api as _common


API_PATH = "/mpstats/ozon/sellerProducts"
SLUG = "linkfox-mpstats-ozon-seller-products"


def _call_with_http_status(call, api_path, params):
    """保留实际 HTTP 状态，供错误解释与认证引导使用。"""
    original_urlopen = _common.urlopen
    status = None

    def capture_status(*args, **kwargs):
        nonlocal status
        try:
            response = original_urlopen(*args, **kwargs)
        except HTTPError as exc:
            status = exc.code
            raise
        status = response.status
        return response

    _common.urlopen = capture_status
    try:
        result = call(api_path, params)
    finally:
        _common.urlopen = original_urlopen
    if isinstance(result, dict) and status is not None:
        result["_http_status"] = status
    return result


def _cwd_output_root():
    """仅在当前工作目录下写入，不使用公共调用器的目录回退。"""
    root = os.path.abspath(os.path.join(os.getcwd(), "linkfox"))
    os.makedirs(root, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    return root


def _prepare_output_directory():
    """请求前确认真正的会话数据目录可写，避免取得结果后才发现路径不可用。"""
    _, session_dir = _common._ensure_session(time.time())
    data_dir = os.path.join(session_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    with tempfile.TemporaryFile(dir=data_dir):
        pass


def _unique_output_path(slug, ts):
    """使用时间戳命名；同秒多次查询时递增微秒，避免覆盖已保存响应。"""
    _, session_dir = _common._ensure_session(ts)
    while os.path.exists(os.path.join(session_dir, "data", f"{slug}-{int(ts * 1_000_000)}.json")):
        ts += 0.000001
    return _common.resolve_data_path(slug, ts)


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    # 目录与文件命名约束由业务入口实现。
    original_root = _common._linkfox_root
    original_output_path = _common._resolve_output_path
    original_call = _common.call_api
    _common._linkfox_root = _cwd_output_root
    _common._resolve_output_path = _unique_output_path
    _common.call_api = lambda path, params: _call_with_http_status(original_call, path, params)
    try:
        if args:
            try:
                _prepare_output_directory()
            except OSError as exc:
                print(f"当前目录不可写，未发起请求：{exc}", file=sys.stderr)
                raise SystemExit(1)
        _common.run(API_PATH, SLUG, argv=args)
    finally:
        _common._linkfox_root = original_root
        _common._resolve_output_path = original_output_path
        _common.call_api = original_call


if __name__ == "__main__":
    main()
