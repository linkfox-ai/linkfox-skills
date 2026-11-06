#!/usr/bin/env python3
"""SIF 关键词竞争概览。

用法：python sif_keyword_overview.py '<JSON 参数>' [--inline] [--no-cache]
完整响应始终落盘；默认使用单层 24 小时缓存。
"""

import json
from pathlib import Path
import sys
import tempfile
import time

import call_api


API_PATH = "/sif/keywordOverview"
SLUG = "linkfox-sif-keyword-overview"


def _prepare_output_root():
    """请求前确认项目输出可写，避免公共调用器回退到其他目录。"""
    cwd = Path.cwd().resolve()
    tmp_root = Path('/tmp').resolve()
    if cwd == tmp_root or tmp_root in cwd.parents:
        raise OSError('禁止将响应保存到 /tmp，请在可写的项目目录运行')
    root = cwd / 'linkfox'
    now = time.time()
    session = call_api._session_id(now)
    data_dir = root / time.strftime('%Y-%m-%d', time.localtime(now)) / session / 'data'
    for directory in (root, data_dir, root / '.cache' / SLUG):
        directory.mkdir(parents=True, exist_ok=True)
        # 使用唯一探针，避免覆盖已有文件；只在目标输出目录内检查。
        with tempfile.TemporaryFile(dir=directory) as probe:
            probe.write(b'')
    return str(root)


def main():
    argv = sys.argv[1:]
    params = [arg for arg in argv if arg not in ('--inline', '--no-cache')]
    # 缺参及非法 JSON 的错误格式、退出码由公共调用器处理。
    if not params:
        return call_api.run(API_PATH, SLUG, argv)
    try:
        json.loads(params[0])
    except json.JSONDecodeError:
        return call_api.run(API_PATH, SLUG, argv)

    try:
        root = _prepare_output_root()
    except OSError as exc:
        print(f'当前项目输出目录不可用：{exc}', file=sys.stderr)
        raise SystemExit(1)

    previous_root = call_api._SESSION_CACHE.get('_root')
    call_api._SESSION_CACHE['_root'] = root
    try:
        # 公共调用器处理缓存键、24 小时 TTL、CLI 和请求传输。
        # 业务入口只使用公共调用器的一层缓存。
        return call_api.run(API_PATH, SLUG, argv)
    finally:
        if previous_root is None:
            call_api._SESSION_CACHE.pop('_root', None)
        else:
            call_api._SESSION_CACHE['_root'] = previous_root


if __name__ == "__main__":
    main()
