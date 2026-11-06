#!/usr/bin/env python3
"""MPSTATS Ozon 商品分日趋势：提供 24 小时缓存，使用公共调用与输出。

用法：python mpstats_ozon_product_trend.py '<JSON 参数>' [--inline] [--no-cache]
完整响应始终保存；小响应全量输出，大响应输出摘要，--inline 强制全量。
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import time

import call_api as api


API_PATH = "/mpstats/ozon/productTrend"
SLUG = "linkfox-mpstats-ozon-product-trend"
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
        if time.time() - os.path.getmtime(path) > CACHE_TTL_SEC:
            return None
        with open(path, encoding="utf-8") as f:
            payload = json.load(f)
        # 缓存直接保存响应对象；损坏的编码、对象或命中元数据均按未命中处理。
        if not isinstance(payload, dict) or not isinstance(payload.get("_cache", {}), dict):
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


def _call_with_http_status(transport, api_path, params):
    """保留本次 HTTP 状态，响应体及错误解释仍由公共调用器提供。"""
    opener = api.urlopen
    status = None

    def observed_urlopen(*args, **kwargs):
        nonlocal status
        try:
            response = opener(*args, **kwargs)
        except api.HTTPError as exc:
            status = exc.code
            raise
        status = response.getcode()
        return response

    api.urlopen = observed_urlopen
    try:
        result = transport(api_path, params)
    finally:
        api.urlopen = opener
    if isinstance(result, dict) and status is not None:
        result["_http_status"] = status
    return result


def _prepare_output_root():
    """在请求前检查 cwd，不回退到其他目录，禁止写入 /tmp。"""
    root = (Path.cwd() / "linkfox").resolve()
    if root == Path("/tmp").resolve() or Path("/tmp").resolve() in root.parents:
        raise OSError("响应目录禁止位于 /tmp")
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    return str(root)


def main(argv=None):
    parser = argparse.ArgumentParser(description="查询 MPSTATS Ozon 商品分日趋势")
    parser.add_argument("params", help="JSON 请求参数")
    parser.add_argument("--inline", action="store_true", help="完整打印并保存响应")
    parser.add_argument("--no-cache", action="store_true", help="禁用 24 小时响应缓存")
    args = parser.parse_args(argv)
    try:
        params = json.loads(args.params)
    except json.JSONDecodeError as exc:
        parser.error(f"JSON 参数格式无效：{exc}")
    if not isinstance(params, dict):
        parser.error("JSON 参数必须为对象")

    try:
        root = _prepare_output_root()
        cache_path = _cache_path(params)
    except OSError as exc:
        print(f"当前目录不可用于保存响应：{exc}", file=sys.stderr)
        return 1

    # 业务层保留唯一一套缓存；公共 run 负责请求、会话元数据和展示。
    transport = api.call_api
    previous_root = api._linkfox_root
    previous_output_path = api._resolve_output_path

    def cached_transport(api_path, request_params):
        result = None if args.no_cache else _load_cache(cache_path)
        if result is None:
            result = _call_with_http_status(transport, api_path, request_params)
            if not args.no_cache:
                _save_cache(cache_path, result)
        return result

    api.call_api = cached_transport
    api._linkfox_root = lambda: root
    api._resolve_output_path = lambda slug, _ts: api.resolve_data_path(slug, time.time())
    try:
        public_argv = [json.dumps(params, ensure_ascii=False), "--no-cache"]
        if args.inline:
            public_argv.append("--inline")
        api.run(API_PATH, SLUG, argv=public_argv)
    finally:
        api.call_api = transport
        api._linkfox_root = previous_root
        api._resolve_output_path = previous_output_path
    return 0


if __name__ == "__main__":
    sys.exit(main())
