#!/usr/bin/env python3
"""睿观外观专利检测，提供 JSON 参数 CLI 和 24 小时本地缓存。

用法：python ruiguan_detection_patent_design.py '<JSON 参数>' [--inline] [--no-cache]
LinkFox 请求、完整响应落盘及摘要通过公共 call_api.run 执行。
"""

import hashlib
import json
import os
import sys
import time

from _ruiguan_common import prepare_output_root, run_gateway
from call_api import get_api_key

API_PATH = '/ruiguan/detectionPatentDesign'
SLUG = 'linkfox-ruiguan-detection-patent-design'
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
        status = None
        if isinstance(payload, dict) and payload.get('_ruiguan_cache_version') == 1:
            status, payload = payload.get('http_status'), payload['body']
        if isinstance(payload, dict):
            payload.setdefault("_cache", {})["hit"] = True
        # 兼容未记录 HTTP 状态的缓存；不为补状态重新发起收费请求。
        return status, payload
    except (OSError, json.JSONDecodeError):
        return None


def _save_cache(path, payload, http_status):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({'_ruiguan_cache_version': 1, 'http_status': http_status,
                       'body': payload}, f, ensure_ascii=False, indent=2)
    except OSError:
        pass



def main():
    argv = sys.argv[1:]
    inline = '--inline' in argv
    use_cache = '--no-cache' not in argv
    argv = [arg for arg in argv if arg not in ('--inline', '--no-cache')]
    if not argv:
        print("用法：ruiguan_detection_patent_design.py '<JSON 参数>' [--inline] [--no-cache]", file=sys.stderr)
        raise SystemExit(1)
    try:
        params = json.loads(argv[0])
    except json.JSONDecodeError as exc:
        print(f'参数 JSON 格式无效：{exc}', file=sys.stderr)
        raise SystemExit(1)
    if not isinstance(params, dict):
        print('参数必须是 JSON 对象', file=sys.stderr)
        raise SystemExit(1)

    try:
        prepare_output_root()
        cache_path = _cache_path(params)
        cached = _load_cache(cache_path) if use_cache else None
        cache_hit = cached is not None
        cached_status, cached_result = cached if cache_hit else (None, None)
        status, result, output = run_gateway(
            API_PATH, SLUG, params, inline=inline, cached_result=cached_result,
            cached_status=cached_status, cache_hit=cache_hit,
        )
    except OSError as exc:
        print(f'无法在当前工作目录保存响应：{exc}', file=sys.stderr)
        raise SystemExit(1)
    if use_cache and not cache_hit:
        _save_cache(cache_path, result, status)
    label = 'Cached HTTP status' if cache_hit else 'HTTP status'
    print(f'{label}: {status if status is not None else "unknown"}'
          + (' (no request made)' if cache_hit else ''), file=sys.stderr)
    print(output, end='')


if __name__ == '__main__':
    main()
