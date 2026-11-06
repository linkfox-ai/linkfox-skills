#!/usr/bin/env python3
"""智慧芽说明书翻译：提供 CLI 和单层缓存，由 call_api.run 调用。

用法：python zhihuiya_description_translated.py '<JSON 参数>' [--inline] [--no-cache]
完整响应始终以 UTF-8 保存；8000 字节以内全量展示，较大响应展示摘要。
"""

import json
import os
from pathlib import Path
import sys
import tempfile
import time

import call_api


API_PATH = "/zhihuiya/descriptionDataTranslated"
SLUG = "linkfox-zhihuiya-description-data-translated"


def _windows_path(path):
    """使用同一文件的 Windows 扩展路径，避免长目录下丢失缓存或响应。"""
    if os.name != 'nt':
        return path
    absolute = os.path.abspath(path)
    if absolute.startswith('\\\\?\\'):
        return absolute
    if absolute.startswith('\\\\'):
        return '\\\\?\\UNC\\' + absolute[2:]
    return '\\\\?\\' + absolute


def _prepare_output():
    """请求前确认当前目录可写；禁止公共调用器回退到其他目录。"""
    cwd = Path.cwd().resolve()
    if cwd == Path('/tmp') or Path('/tmp') in cwd.parents:
        raise OSError('禁止在 /tmp 下保存响应，请切换到项目目录')
    root = cwd / 'linkfox'
    root.mkdir(parents=True, exist_ok=True)
    call_api._SESSION_CACHE['_root'] = _windows_path(str(root))
    # 同时预检实际会话数据目录，以免请求成功后才发现无法落盘。
    _, session_dir = call_api._ensure_session(time.time())
    data_dir = Path(session_dir) / 'data'
    data_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=data_dir) as probe:
        probe.write(b'')


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    usage = "用法：zhihuiya_description_translated.py '<JSON 参数>' [--inline] [--no-cache]"
    if argv == ['--help'] or argv == ['-h']:
        print(usage)
        return
    positional = [a for a in argv if a not in ('--inline', '--no-cache')]
    if not positional:
        print(usage, file=sys.stderr)
        raise SystemExit(1)
    try:
        json.loads(positional[0])
    except json.JSONDecodeError as exc:
        print(f'参数 JSON 格式错误：{exc}', file=sys.stderr)
        raise SystemExit(1)
    try:
        _prepare_output()
    except OSError as exc:
        print(f'当前目录无法保存响应：{exc}', file=sys.stderr)
        raise SystemExit(1)
    # 使用公共调用器的 24 小时缓存，不另建缓存层。
    original_cache_path = call_api._cache_path
    try:
        call_api._cache_path = lambda slug, params: _windows_path(
            original_cache_path(slug, params)
        )
        call_api.run(API_PATH, SLUG, argv=argv)
    finally:
        call_api._cache_path = original_cache_path


if __name__ == '__main__':
    main()
