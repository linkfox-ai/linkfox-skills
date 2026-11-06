#!/usr/bin/env python3
"""卖大律产品侵权检测 CLI；提供 24 小时缓存，复用公共调用器。

python maidalv_check_api_flash.py '<JSON 参数>' [--inline] [--no-cache]
"""

import json
import hashlib
import os
from pathlib import Path
import sys
import time

from api_support import invoke_api, save_response, prepare_root, normal_response
import call_api as common_api

API_PATH = '/maidalv/checkApiFlash'
SLUG = 'linkfox-maidalv-product-tro-detection'
SMALL_THRESHOLD = 8000
CACHE_TTL_SEC = 24 * 60 * 60
_LAST_OUTPUT_PATH = None

get_api_base = common_api.get_api_base
get_api_key = common_api.get_api_key
summarize = common_api.summarize


def call_api(params):
    global _LAST_OUTPUT_PATH
    status, result, _LAST_OUTPUT_PATH, _log = invoke_api(API_PATH, SLUG, params)
    if isinstance(result, dict):
        # 业务字段原样保存，并附加本地传输元数据供响应判断使用。
        # 否则 HTTP 401 等响应即使正文缺少 errcode，也会丢失失败依据。
        result = dict(result, _transportHttpStatus=status)
        Path(_LAST_OUTPUT_PATH).write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8'
        )
    else:
        print(f'响应格式异常：HTTP {status}，完整原始 JSON 已保存', file=sys.stderr)
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
            cache_meta = payload.get('_cache')
            payload['_cache'] = dict(cache_meta, hit=True) if isinstance(cache_meta, dict) else {'hit': True}
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
    global _LAST_OUTPUT_PATH
    _LAST_OUTPUT_PATH = None
    argv = list(sys.argv[1:] if argv is None else argv)
    if '--help' in argv or '-h' in argv:
        print("用法：maidalv_check_api_flash.py '<JSON 参数>' [--inline] [--no-cache]")
        return 0
    inline = '--inline' in argv
    use_cache = '--no-cache' not in argv
    argv = [a for a in argv if a not in ('--inline', '--no-cache')]
    if not argv:
        print("用法：maidalv_check_api_flash.py '<JSON 参数>' [--inline] [--no-cache]", file=sys.stderr)
        return 1
    try:
        params = json.loads(argv[0])
    except json.JSONDecodeError as exc:
        print(f'JSON 参数格式错误：{exc}', file=sys.stderr)
        return 1
    if not isinstance(params, dict):
        print('JSON 参数必须为对象', file=sys.stderr)
        return 1
    try:
        prepare_root()
        cache_path = _cache_path(params)
        result = _load_cache(cache_path) if use_cache else None
        if result is None:
            result = call_api(params)
            if use_cache:
                _save_cache(cache_path, result)
        out_path = _LAST_OUTPUT_PATH or save_response(SLUG, result)
        serialized = json.dumps(result, ensure_ascii=False, indent=2)
        print(f'Saved full response: {out_path} ({len(serialized.encode("utf-8"))} bytes)')
        if isinstance(result, dict) and '_transportHttpStatus' in result:
            status = result['_transportHttpStatus']
            print(f'HTTP 状态：{status}', file=sys.stderr)
            if not normal_response(status, result):
                print('未正常响应，请按 references/api.md 处理；不自动重试', file=sys.stderr)
        cache_meta = result.get('_cache') if isinstance(result, dict) else None
        if isinstance(cache_meta, dict) and cache_meta.get('hit'):
            print(f'Cache hit: {cache_path}', file=sys.stderr)
            if '_transportHttpStatus' not in result:
                print('旧缓存未记录 HTTP 状态，不能据此确认请求正常；保留缓存且不自动重试', file=sys.stderr)
        if inline or len(serialized.encode('utf-8')) <= SMALL_THRESHOLD:
            print(serialized)
        else:
            summarize(result)
        return 0
    except (OSError, ValueError) as exc:
        print(f'执行失败：{exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
