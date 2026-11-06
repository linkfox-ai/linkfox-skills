#!/usr/bin/env python3
"""智慧芽外观专利图片检索；提供 JSON CLI、24 小时本地缓存和完整响应输出。"""

import json
import hashlib
import os
import sys
import time

import call_api as gateway
from patent_runtime import run_gateway

API_PATH = "/zhihuiya/patentImageSearch"
SLUG = "linkfox-zhihuiya-patent-image-search"
PATENT_TYPE = "D"
ALLOWED_MODELS = {1, 2}
DEFAULT_MODEL = 1
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
            # 损坏的缓存元数据按未命中处理，不在发起请求前崩溃。
            if not isinstance(payload.get("_cache", {}), dict):
                return None
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
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or "--help" in argv or "-h" in argv:
        print("用法: zhihuiya_patent_image_search.py '<JSON 参数>' [--inline] [--no-cache]",
              file=sys.stderr)
        return 0 if argv else 1
    inline = "--inline" in argv
    use_cache = "--no-cache" not in argv
    args = [a for a in argv if a not in ("--inline", "--no-cache")]
    if len(args) != 1:
        print("需要一个 JSON 对象参数。", file=sys.stderr)
        return 1
    try:
        params = json.loads(args[0])
    except json.JSONDecodeError as exc:
        print(f"参数 JSON 格式错误: {exc}", file=sys.stderr)
        return 1
    if not isinstance(params, dict):
        print("参数必须是 JSON 对象。", file=sys.stderr)
        return 1

    # 强制纠正专利类型，缺省模型为 1，在请求前拒绝实用新型模型。
    params["patentType"] = PATENT_TYPE
    if params.get("model") is None:
        params["model"] = DEFAULT_MODEL
    elif type(params["model"]) is not int or params["model"] not in ALLOWED_MODELS:
        print("本技能仅支持外观设计专利（model 必须为 1 或 2）；"
              "实用新型检索请使用 linkfox-zhihuiya-utility-patent-image-search。",
              file=sys.stderr)
        return 1
    if not isinstance(params.get("url"), str) or not params["url"].strip():
        print("请提供公开可访问的图片 url。", file=sys.stderr)
        return 1

    def cached_transport(path, body):
        cache_path = _cache_path(body) if use_cache else None
        result = _load_cache(cache_path) if use_cache else None
        if result is not None:
            # 缓存未记录 HTTP 状态；仅复用响应体，不据此宣称业务成功。
            print(f"Cache hit: {cache_path}", file=sys.stderr)
            print("缓存响应：历史 HTTP 状态未知。", file=sys.stderr)
            return None, result
        status, result = gateway_transport(path, body)
        if status is None:
            print("未收到 HTTP 响应；连接失败原因见响应体。", file=sys.stderr)
        else:
            print(f"HTTP {status}", file=sys.stderr)
        if use_cache:
            _save_cache(cache_path, result)
        return status, result

    gateway_transport = gateway.call_api
    try:
        run_gateway(API_PATH, SLUG, params, inline=inline, transport=cached_transport)
    except OSError as exc:
        print(f"当前目录数据保存失败: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
