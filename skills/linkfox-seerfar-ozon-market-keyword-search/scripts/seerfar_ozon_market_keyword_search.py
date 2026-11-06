#!/usr/bin/env python3
"""Seerfar Ozon 市场热词搜索：使用公共调用、24 小时缓存和输出流程。

用法：python seerfar_ozon_market_keyword_search.py '<JSON 参数>' [--inline] [--no-cache]
业务入口在请求前检查当前目录及会话数据路径，并保留 HTTP 状态；不实现额外缓存或 HTTP 请求。
"""

import json
from pathlib import Path
import sys
import tempfile

import call_api as _runner


API_PATH = "/seerfar/ozon/marketKeywordSearch"
SLUG = "linkfox-seerfar-ozon-market-keyword-search"
SMALL_THRESHOLD = _runner.SMALL_THRESHOLD
CACHE_TTL_SEC = _runner.CACHE_TTL_SEC
get_api_base = _runner.get_api_base
get_api_key = _runner.get_api_key
_BASE_CALL_API = _runner.call_api


def _call_api_with_status(api_path, params):
    """复用公共请求逻辑，保留其解析 JSON 后不再返回的 HTTP 状态。"""
    original_urlopen = _runner.urlopen
    http_status = None

    def record_status(*args, **kwargs):
        nonlocal http_status
        try:
            response = original_urlopen(*args, **kwargs)
        except _runner.HTTPError as exc:
            http_status = exc.code
            raise
        http_status = response.status
        return response

    _runner.urlopen = record_status
    try:
        result = _BASE_CALL_API(api_path, params)
    finally:
        _runner.urlopen = original_urlopen
    if isinstance(result, dict) and http_status is not None:
        result['_http_status'] = http_status
    return result


def _output_root():
    """请求前确认 cwd 可写；禁止公共调用器回退到其他目录。"""
    cwd = Path.cwd().resolve()
    forbidden = Path('/tmp').resolve()
    if cwd == forbidden or forbidden in cwd.parents:
        raise OSError('禁止在 /tmp 下保存任务数据，请切换到可写的项目目录')
    # 先检查 cwd 本身；已有可写 linkfox 目录不能掩盖 cwd 不可写。
    with tempfile.TemporaryFile(dir=cwd):
        pass
    root = cwd / 'linkfox'
    root.mkdir(exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    return str(root)


def _prepare_session_output():
    """提前验证实际输出目录与元数据，避免请求后才发现会话路径不可写。"""
    _, session_dir = _runner._ensure_session(_runner.time.time())
    session = Path(session_dir)
    with tempfile.TemporaryFile(dir=session):
        pass
    data_dir = session / 'data'
    data_dir.mkdir(exist_ok=True)
    with tempfile.TemporaryFile(dir=data_dir):
        pass
    # 公共调用器会更新已有元数据；目录可写不代表该文件可写。
    with (session / '_meta.json').open('r+', encoding='utf-8'):
        pass


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv in (['--help'], ['-h']):
        print("用法：seerfar_ozon_market_keyword_search.py '<JSON 参数>' [--inline] [--no-cache]")
        return
    # 无参数或非法 JSON 由公共 CLI 处理，避免为错误输入创建目录。
    payload_args = [a for a in argv if a not in ('--inline', '--no-cache')]
    if not payload_args:
        return _runner.run(API_PATH, SLUG, argv=argv)
    try:
        json.loads(payload_args[0])
    except json.JSONDecodeError:
        return _runner.run(API_PATH, SLUG, argv=argv)
    try:
        root = _output_root()
    except OSError as exc:
        print(f'当前目录不可写或不允许落盘：{exc}', file=sys.stderr)
        raise SystemExit(1)
    # 仅为此次业务调用指定输出根目录。
    previous = _runner._SESSION_CACHE.get('_root')
    previous_call_api = _runner.call_api
    _runner._SESSION_CACHE['_root'] = root
    try:
        try:
            _prepare_session_output()
        except OSError as exc:
            print(f'会话数据路径不可写或不允许落盘：{exc}', file=sys.stderr)
            raise SystemExit(1)
        _runner.call_api = _call_api_with_status
        return _runner.run(API_PATH, SLUG, argv=argv)
    finally:
        _runner.call_api = previous_call_api
        if previous is None:
            _runner._SESSION_CACHE.pop('_root', None)
        else:
            _runner._SESSION_CACHE['_root'] = previous


if __name__ == '__main__':
    main()
