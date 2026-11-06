#!/usr/bin/env python3
"""睿观图片政策合规检测，提供 JSON 参数 CLI、24 小时业务缓存与会话输出。"""

import argparse
import hashlib
import json
import os
import sys
import time

import call_api as api
from _ruiguan_common import run_request

API_PATH = "/ruiguan/gunPartsSearch"
SLUG = "linkfox-ruiguan-gun-parts-search"
CACHE_TTL_SEC = 24 * 60 * 60


def _cache_key(params):
    raw = json.dumps(params, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _cache_path(params):
    path = os.path.join(os.getcwd(), "linkfox", ".cache", SLUG)
    os.makedirs(path, exist_ok=True)
    return os.path.join(path, f"{SLUG}-{_cache_key(params)}.json")


def _load_cache(path):
    try:
        if not os.path.isfile(path):
            return None
        if time.time() - os.path.getmtime(path) > CACHE_TTL_SEC:
            return None
        with open(path, encoding="utf-8") as f:
            payload = json.load(f)
        if isinstance(payload, dict):
            # 损坏的缓存元数据不能使整个 CLI 崩溃，也不能算有效命中。
            if "_cache" in payload and not isinstance(payload["_cache"], dict):
                return None
            payload.setdefault("_cache", {})["hit"] = True
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
    parser = argparse.ArgumentParser(description="睿观图片政策合规检测")
    parser.add_argument("params", help="检测请求体 JSON")
    parser.add_argument("--inline", action="store_true", help="完整打印响应，同时落盘")
    parser.add_argument("--no-cache", action="store_true", help="不读取或写入业务缓存")
    args = parser.parse_args(argv)
    try:
        params = json.loads(args.params)
    except json.JSONDecodeError as exc:
        parser.error(f"JSON 参数无效：{exc}")
    if not isinstance(params, dict):
        parser.error("请求体必须是 JSON 对象")
    image_url = params.get("imageUrl")
    if not isinstance(image_url, str) or not image_url.strip() or len(image_url) > 1000:
        parser.error("imageUrl 必须是非空字符串，且长度不超过 1000 字符")

    # 业务缓存直接保存原始响应；公共 run 强制 --no-cache，避免出现两层缓存。
    transport = api.call_api

    def with_legacy_cache(path, body):
        cache_path = _cache_path(body) if not args.no_cache else None
        cached = _load_cache(cache_path) if cache_path else None
        if cached is not None:
            # 业务缓存不记录 HTTP 状态，不能将缓存命中当作接口成功。
            return None, cached
        status, result = transport(path, body)
        if status is not None:
            print(f"HTTP status: {status}", file=sys.stderr)
        if cache_path:
            _save_cache(cache_path, result)
        return status, result

    try:
        run_request(API_PATH, SLUG, params, inline=args.inline, transport=with_legacy_cache)
    except OSError as exc:
        parser.exit(1, f"无法保存会话数据：{exc}\n")


if __name__ == "__main__":
    main()
