#!/usr/bin/env python3
"""MPSTATS Ozon 品牌商品查询。

用法：python mpstats_ozon_brand_products.py '<JSON 参数>' [--inline] [--no-cache]
提供 24 小时缓存、完整响应落盘及按大小输出结果；HTTP 由公共调用器执行。
"""

import json
import os
import sys
import tempfile
from pathlib import Path

import call_api


API_PATH = '/mpstats/ozon/brandProducts'
SLUG = 'linkfox-mpstats-ozon-brand-products'


def _prepare_output_root():
    """将输出限定在 cwd；提前检查实际数据目录，避免请求后才发现不可写。"""
    root = Path.cwd() / 'linkfox'
    now = call_api.time.time()
    sid = call_api._session_id(now)
    date = call_api.time.strftime('%Y-%m-%d', call_api.time.localtime(now))
    data_dir = root / date / sid / 'data'
    data_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=data_dir) as probe:
        probe.write(b'')
    # 通过公共调用器的进程内根目录配置禁止其他目录回退。
    call_api._SESSION_CACHE['_root'] = os.fspath(root)


def _resolve_output_path(slug, _timestamp):
    """保留微秒精度，避免同一秒内的多次查询覆盖完整响应。"""
    return call_api.resolve_data_path(slug, call_api.time.time())


def _call_preserving_http_status(caller, api_path, params):
    """保留公共调用器解码前的 HTTP 状态，不改写响应体的业务码。"""
    previous_urlopen = call_api.urlopen
    status = None

    def tracked_urlopen(*args, **kwargs):
        nonlocal status
        try:
            response = previous_urlopen(*args, **kwargs)
        except call_api.HTTPError as exc:
            status = exc.code
            raise
        status = response.getcode()
        return response

    try:
        call_api.urlopen = tracked_urlopen
        result = caller(api_path, params)
    finally:
        call_api.urlopen = previous_urlopen
    if isinstance(result, dict) and status is not None:
        result['_http_status'] = status
    return result


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if '--help' in argv or '-h' in argv:
        print("用法：python mpstats_ozon_brand_products.py '<JSON 参数>' [--inline] [--no-cache]")
        print('默认复用 24 小时缓存；--inline 全量输出；--no-cache 禁用缓存读写。')
        return

    params = [arg for arg in argv if arg not in ('--inline', '--no-cache')]
    if params:
        try:
            json.loads(params[0])
        except json.JSONDecodeError:
            # 保持公共 CLI 的错误输出及退出码，错误参数不创建数据目录。
            return call_api.run(API_PATH, SLUG, argv)
        try:
            _prepare_output_root()
        except OSError as exc:
            print(f'当前目录的数据路径不可写：{exc}', file=sys.stderr)
            raise SystemExit(1)
    # 缓存路径、键和 TTL 由公共调用器统一管理，业务封装不单独缓存。
    previous_resolver = call_api._resolve_output_path
    previous_caller = call_api.call_api
    try:
        # 在业务封装内设置文件名精度，调用后恢复公共调用器的路径解析函数。
        call_api._resolve_output_path = _resolve_output_path
        call_api.call_api = lambda path, body: _call_preserving_http_status(previous_caller, path, body)
        return call_api.run(API_PATH, SLUG, argv)
    finally:
        call_api._resolve_output_path = previous_resolver
        call_api.call_api = previous_caller


if __name__ == '__main__':
    main()
