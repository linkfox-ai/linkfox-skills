#!/usr/bin/env python3
"""AI 图片生成：JSON 参数 CLI、24 小时业务缓存及会话输出。"""

import hashlib
import json
import os
import sys
import time

import _image_gateway

API_PATH = "/multimodal/generateImage"
SLUG = "linkfox-multimodal-generate-image"
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
        if not isinstance(payload, dict):
            return None
        # 本地标记损坏时修复标记，继续复用已缓存的业务结果，避免重复付费。
        if not isinstance(payload.get("_cache"), dict):
            payload["_cache"] = {}
        payload["_cache"]["hit"] = True
        return payload
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None


def _save_cache(path, payload):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv in (["--help"], ["-h"]):
        print("用法: multimodal_generate_image.py '<JSON 参数>' [--inline] [--no-cache]")
        return
    inline = "--inline" in argv
    use_cache = "--no-cache" not in argv
    argv = [a for a in argv if a not in ("--inline", "--no-cache")]
    if not argv:
        print("用法: multimodal_generate_image.py '<JSON 参数>' [--inline] [--no-cache]", file=sys.stderr)
        raise SystemExit(1)
    try:
        params = json.loads(argv[0])
    except json.JSONDecodeError as exc:
        print(f"参数 JSON 格式错误: {exc}", file=sys.stderr)
        raise SystemExit(1)
    if not isinstance(params, dict):
        print("JSON 参数必须为对象", file=sys.stderr)
        raise SystemExit(1)
    cache_path = _cache_path(params)
    cached = _load_cache(cache_path) if use_cache else None
    _image_gateway.run(
        API_PATH, SLUG, params, inline=inline, cached=cached,
        on_response=(lambda result: _save_cache(cache_path, result)) if use_cache else None,
    )


if __name__ == "__main__":
    main()
