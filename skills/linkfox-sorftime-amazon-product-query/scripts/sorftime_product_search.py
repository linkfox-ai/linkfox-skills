#!/usr/bin/env python3
"""Sorftime 亚马逊产品搜索：使用本地缓存，通过公共调用器请求与归档。

用法：python sorftime_product_search.py '<JSON 参数>' [--inline] [--no-cache]
默认启用 24 小时本地缓存；--no-cache 禁用读写，--inline 强制全量打印。
完整响应始终按会话保存为 UTF-8，超过 8000 字节时默认展示摘要。
"""

import hashlib
import json
import os
import secrets
import sys
import time
from unittest.mock import patch

import call_api as api_client

API_PATH = "/sorftime/amazon/productQuery"
SLUG = "linkfox-sorftime-amazon-product-query"
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
    try:
        if not os.path.isfile(path):
            return None
        if time.time() - os.path.getmtime(path) > CACHE_TTL_SEC:
            return None
        with open(path, encoding="utf-8") as f:
            payload = json.load(f)
        if isinstance(payload, dict):
            if "_cache" in payload and not isinstance(payload["_cache"], dict):
                return None
            payload.setdefault("_cache", {})["hit"] = True
        return payload
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None


def _save_cache(path, payload):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def _linkfox_root():
    """在当前目录归档；不可写时在请求前报错。"""
    cwd = os.path.realpath(os.getcwd())
    if cwd == "/tmp" or cwd.startswith("/tmp/"):
        raise PermissionError("当前目录位于 /tmp，请切换到任务工作目录")
    root = os.path.abspath(os.path.join(cwd, "linkfox"))
    os.makedirs(root, exist_ok=True)
    probe = os.path.join(root, f".write_probe-{secrets.token_hex(6)}")
    with open(probe, "w", encoding="utf-8"):
        pass
    os.remove(probe)
    return root


def _resolve_output_path(slug, _ts):
    """按会话归档，使用微秒时间戳避免同秒结果相互覆盖。"""
    return api_client.resolve_data_path(slug, time.time())


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    usage = "用法：sorftime_product_search.py '<JSON 参数>' [--inline] [--no-cache]"
    if argv in (["--help"], ["-h"]):
        print(usage)
        return
    inline = "--inline" in argv
    use_cache = "--no-cache" not in argv
    argv = [a for a in argv if a not in ("--inline", "--no-cache")]
    if not argv:
        print(usage, file=sys.stderr)
        raise SystemExit(1)
    try:
        params = json.loads(argv[0])
    except json.JSONDecodeError as exc:
        print(f"参数 JSON 格式无效：{exc}", file=sys.stderr)
        raise SystemExit(1)

    # 先检查当前工作目录，防止请求之后才发现无法归档；不采用公共回退目录。
    try:
        _linkfox_root()
        cache_path = _cache_path(params)
    except OSError as exc:
        print(f"当前目录无法保存数据：{exc}", file=sys.stderr)
        raise SystemExit(1)
    cached = _load_cache(cache_path) if use_cache else None
    transport = api_client.call_api

    def cached_request(api_path, request_params):
        if cached is not None:
            return cached
        result = transport(api_path, request_params)
        if use_cache:
            _save_cache(cache_path, result)
        return result

    # run 统一负责 HTTP、错误体解析、归档和输出。仅使用业务封装的缓存层。
    run_argv = [json.dumps(params, ensure_ascii=False), "--no-cache"]
    if inline:
        run_argv.append("--inline")
    with patch.object(api_client, "call_api", cached_request), patch.object(
        api_client, "_linkfox_root", _linkfox_root
    ), patch.object(
        api_client, "_resolve_output_path", _resolve_output_path
    ):
        api_client.run(API_PATH, SLUG, run_argv)


if __name__ == "__main__":
    main()
