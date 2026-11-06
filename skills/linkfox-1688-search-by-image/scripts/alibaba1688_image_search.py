#!/usr/bin/env python3
"""1688 以图搜图：参数缓存、WebP 预处理、CLI 与完整响应落盘。"""

import hashlib
import json
import os
import sys
import time

import call_api as api
from _image_prepare import ImagePreparationError, prepare_search_params
from _linkfox_runner import ensure_output_root, run_request

API_PATH = '/alibaba1688/imageSearch'
SLUG = 'linkfox-1688-search-by-image'
CACHE_TTL_SEC = 24 * 60 * 60


def call_api(params):
    """Python 调用入口：完成图片预处理后返回响应对象。"""
    _, result = run_request(API_PATH, SLUG, params,
                            transform=prepare_search_params, quiet=True)
    return result


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
        if isinstance(payload, dict):
            if not isinstance(payload.get("_cache"), dict):
                payload["_cache"] = {}
            payload.setdefault("_cache", {})["hit"] = True
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
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    argv = list(sys.argv[1:] if argv is None else argv)
    usage = "用法: alibaba1688_image_search.py '<JSON 参数>' [--inline] [--no-cache]"
    if '--help' in argv or '-h' in argv:
        print(usage)
        return 0
    inline = '--inline' in argv
    use_cache = '--no-cache' not in argv
    argv = [arg for arg in argv if arg not in ('--inline', '--no-cache')]
    if not argv:
        print(usage, file=sys.stderr)
        return 1
    try:
        params = json.loads(argv[0])
        if not isinstance(params, dict):
            raise ValueError('参数必须是 JSON 对象')
    except ValueError as exc:
        print(f'参数格式无效: {exc}', file=sys.stderr)
        return 1
    try:
        ensure_output_root()
        cache_path = _cache_path(params)
        cached = _load_cache(cache_path) if use_cache else None
        run_request(API_PATH, SLUG, params, transform=prepare_search_params,
                    cached=cached, inline=inline,
                    on_result=(lambda payload: _save_cache(cache_path, payload))
                    if use_cache else None)
    except ImagePreparationError as exc:
        print(f'图片预处理失败: {exc}', file=sys.stderr)
        return 1
    except OSError as exc:
        print(f'当前目录保存失败: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
