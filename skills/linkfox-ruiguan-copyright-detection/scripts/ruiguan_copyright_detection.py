#!/usr/bin/env python3
"""睿观图片版权检测；支持 JSON CLI、24 小时响应体缓存和会话输出。"""

import argparse
import hashlib
import json
import os
import sys
import time

import call_api as api
from _ruiguan_common import run_request

API_PATH = "/ruiguan/copyrightDetection"
SLUG = "linkfox-ruiguan-copyright-detection"
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
        if isinstance(payload, dict):
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
    parser = argparse.ArgumentParser(description="睿观图片版权检测")
    parser.add_argument("params", help="JSON 参数对象")
    parser.add_argument("--inline", action="store_true", help="保存并完整打印响应")
    parser.add_argument("--no-cache", action="store_true", help="禁用缓存读取和写入")
    args = parser.parse_args(argv)
    try:
        params = json.loads(args.params)
        if not isinstance(params, dict):
            raise ValueError("参数必须为 JSON 对象")
    except ValueError as exc:
        print(f"参数格式错误: {exc}", file=sys.stderr)
        return 1

    transport = api.call_api

    def cached_transport(path, body):
        cache_path = _cache_path(body) if not args.no_cache else None
        result = _load_cache(cache_path) if cache_path else None
        if result is not None:
            print(f"Cache hit: {cache_path}", file=sys.stderr)
            # 缓存只存响应体，不包含 HTTP 状态；不对外补造状态字段。
            return None, result
        status, result = transport(path, body)
        if cache_path:
            _save_cache(cache_path, result)
        return status, result

    try:
        run_request(API_PATH, SLUG, params, inline=args.inline, transport=cached_transport)
    except OSError as exc:
        print(f"当前目录无法保存数据: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
