#!/usr/bin/env python3
"""图片识别 CLI：使用 24 小时缓存，公共 run 负责请求、落盘和输出。"""
import hashlib
import json
import os
import sys
import time
import call_api as api
from _image_runtime import run_request

API_PATH = "/multimodal/recognizeImage"
SLUG = "linkfox-multimodal-recognize-image"
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


def _save_cache(path, payload, http_status):
    if isinstance(payload, dict):
        payload = dict(payload, _http_status=http_status)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def main():
    argv = sys.argv[1:]
    if not argv or "--help" in argv or "-h" in argv:
        print("用法: multimodal_recognize_image.py '<JSON 参数>' [--inline] [--no-cache]",
              file=sys.stdout if argv else sys.stderr)
        return 0 if argv else 1
    inline = "--inline" in argv
    use_cache = "--no-cache" not in argv
    argv = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    if len(argv) != 1:
        print("请提供一个 JSON 参数对象", file=sys.stderr)
        return 1
    try:
        params = json.loads(argv[0])
    except json.JSONDecodeError as e:
        print(f"JSON 参数格式错误: {e}", file=sys.stderr)
        return 1
    if not isinstance(params, dict):
        print("JSON 参数必须是对象", file=sys.stderr)
        return 1
    try:
        path = _cache_path(params)
        cached = _load_cache(path) if use_cache else None
        transport = api.call_api

        def with_original_cache(api_path, request_params):
            if cached is not None:
                print(f"Cache hit: {path}", file=sys.stderr)
                # 历史缓存未记录 HTTP 状态时保持未知，不推断为成功。
                status = cached.get("_http_status") if isinstance(cached, dict) else None
                return status, cached
            status, result = transport(api_path, request_params)
            # 缓存直接保存响应体，错误与空响应同样可复用。
            if use_cache:
                _save_cache(path, result, status)
            return status, result

        run_request(API_PATH, SLUG, params, transport=with_original_cache, inline=inline)
        return 0
    except OSError as e:
        print(f"无法在当前目录保存响应: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
