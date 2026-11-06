#!/usr/bin/env python3
"""Temu 商品查询 CLI；由公共调用器负责传输、单层缓存和结果输出。

用法：python temu_product_query.py '<JSON 参数>' [--inline] [--no-cache]
默认保留 24 小时缓存；完整响应始终保存，小结果全量输出，大结果输出摘要。
"""

import json
import os
from pathlib import Path
import sys
import tempfile
import time

import call_api


API_PATH = '/ehunt/temu/productQuery'
SLUG = 'linkfox-temu-product-query'


def _call_with_http_status(transport, api_path, params):
    """保留传输层状态，避免 JSON 错误体掩盖认证或路径错误。"""
    original_open = call_api.urlopen
    status = None

    def open_with_status(*args, **kwargs):
        nonlocal status
        try:
            response = original_open(*args, **kwargs)
        except call_api.HTTPError as exc:
            status = exc.code
            raise
        status = response.getcode()
        return response

    call_api.urlopen = open_with_status
    try:
        result = transport(api_path, params)
    finally:
        call_api.urlopen = original_open
    if isinstance(result, dict) and status is not None:
        result['_http_status'] = status
    return result


def _prepare_output_root():
    """请求前确认当前目录可写，禁止公共调用器回退到其他目录。"""
    root = Path.cwd() / 'linkfox'
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    return str(root.resolve())


def _prepare_session_output():
    """请求前检查实际会话数据目录，避免请求完成后才发现路径阻塞。"""
    _, session_dir = call_api._ensure_session(time.time())
    data_dir = Path(session_dir) / 'data'
    data_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=data_dir):
        pass
    # 已有元数据也必须可写；公共调用器会在保存响应时更新它。
    with (Path(session_dir) / '_meta.json').open('a', encoding='utf-8'):
        pass


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv in (['--help'], ['-h']):
        print("用法：temu_product_query.py '<JSON 参数>' [--inline] [--no-cache]")
        print('默认使用 24 小时缓存；--no-cache 禁止读写缓存；--inline 强制全量输出。')
        return

    # 公共调用器处理缺参及 JSON 解析错误；错误输入不建目录。
    arguments = [arg for arg in argv if arg not in ('--inline', '--no-cache')]
    if not arguments:
        return call_api.run(API_PATH, SLUG, argv=argv)
    try:
        json.loads(arguments[0])
    except json.JSONDecodeError:
        return call_api.run(API_PATH, SLUG, argv=argv)

    try:
        output_root = _prepare_output_root()
    except OSError as exc:
        print(f'当前工作目录不可写：{exc}', file=sys.stderr)
        raise SystemExit(1)

    # 支持备用网关与路径配置；标准网关变量和双密钥按约定优先级读取。
    original_base = os.environ.get('LINKFOX_TOOL_GATEWAY')
    legacy_base = os.environ.get('LINKFOX_TOOL_GATEWAY_BASE')
    original_root = call_api._SESSION_CACHE.get('_root')
    original_transport = call_api.call_api
    if not original_base and legacy_base:
        os.environ['LINKFOX_TOOL_GATEWAY'] = legacy_base
    path = os.environ.get('LINKFOX_EHUNT_TEMU_PRODUCT_QUERY_PATH') or API_PATH
    path = '/' + path.lstrip('/')
    call_api._SESSION_CACHE['_root'] = output_root
    try:
        try:
            _prepare_session_output()
        except OSError as exc:
            print(f'会话数据目录不可写：{exc}', file=sys.stderr)
            raise SystemExit(1)
        # run 统一管理响应缓存，避免建立第二层缓存。
        call_api.call_api = lambda api_path, params: _call_with_http_status(
            original_transport, api_path, params)
        return call_api.run(path, SLUG, argv=argv)
    finally:
        call_api.call_api = original_transport
        if original_base is None:
            os.environ.pop('LINKFOX_TOOL_GATEWAY', None)
        else:
            os.environ['LINKFOX_TOOL_GATEWAY'] = original_base
        if original_root is None:
            call_api._SESSION_CACHE.pop('_root', None)
        else:
            call_api._SESSION_CACHE['_root'] = original_root


if __name__ == '__main__':
    main()
