#!/usr/bin/env python3
"""睿观图形商标检测；提供 24 小时缓存及 JSON CLI。

用法：python ruiguan_trademark_graphic_detection.py '<JSON 参数>' [--inline] [--no-cache]
完整响应始终落盘；小响应全量打印，大响应打印摘要。
"""

import hashlib
import json
import os
import sys
import time

import call_api as api
from call_api import run
from _runtime import output_in_cwd, response_object, response_with_status

API_PATH = '/ruiguan/trademarkGraphicDetection'
SLUG = 'linkfox-ruiguan-trademark-graphic-detection'
CACHE_TTL_SEC = 24 * 60 * 60


def _cache_key(params):
    raw = json.dumps(params, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _cache_path(params):
    cwd = os.getcwd()
    path = os.path.join(cwd, "linkfox", ".cache", SLUG)
    os.makedirs(path, exist_ok=True)
    return os.path.join(path, f"{SLUG}-{_cache_key(params)}.json")


def _load_cache(path):
    if not os.path.isfile(path):
        return None
    if time.time() - os.path.getmtime(path) > CACHE_TTL_SEC:
        return None
    try:
        with open(path, encoding="utf-8") as f:
            payload = json.load(f)
        payload = response_object(payload)
        # 兼容未记录传输状态的历史原始响应缓存，不能推定当时 HTTP 为 200。
        payload.setdefault('_http_status', None)
        if not isinstance(payload.get('_cache'), dict):
            payload['_cache'] = {}
        payload['_cache']['hit'] = True
        return payload
    except (OSError, json.JSONDecodeError):
        return None


def _save_cache(path, payload):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv == ['--help'] or argv == ['-h']:
        print(__doc__)
        return
    params_args = [arg for arg in argv if arg not in ('--inline', '--no-cache')]
    if params_args:
        try:
            if not isinstance(json.loads(params_args[0]), dict):
                raise ValueError('参数必须为 JSON 对象')
        except (ValueError, json.JSONDecodeError) as exc:
            print(f'参数格式错误：{exc}', file=sys.stderr)
            raise SystemExit(1)

    # 公共 run 使用本脚本的缓存函数：读写原始响应格式，沿用参数哈希键、
    # 24 小时 TTL 和命中提示，不叠加第二层响应缓存。
    original = api._cache_path, api._load_cache, api._save_cache, api.call_api
    transport = api.call_api

    def capture(path, params):
        status, payload = transport(path, params)
        return status, response_with_status(status, payload)

    api._cache_path = lambda _slug, params: _cache_path(params)
    api._load_cache = _load_cache
    api._save_cache = lambda path, payload, _status: _save_cache(path, payload)
    api.call_api = capture
    try:
        with output_in_cwd():
            run(API_PATH, SLUG, argv=argv)
    finally:
        api._cache_path, api._load_cache, api._save_cache, api.call_api = original


if __name__ == '__main__':
    main()
