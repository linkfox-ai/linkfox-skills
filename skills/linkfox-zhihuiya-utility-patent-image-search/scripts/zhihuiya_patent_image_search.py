#!/usr/bin/env python3
"""实用新型专利图片检索，提供 CLI、参数归一化及 24 小时业务缓存。"""

import hashlib
import json
import os
import sys
import time

import call_api as api
from _patent_runtime import response_output, run_request

API_PATH = "/zhihuiya/patentImageSearch"
SLUG = "linkfox-zhihuiya-utility-patent-image-search"
PATENT_TYPE = "U"
ALLOWED_MODELS = {3, 4}
DEFAULT_MODEL = 4
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
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--help" in argv or "-h" in argv:
        print("用法: zhihuiya_patent_image_search.py '<JSON 参数>' [--inline] [--no-cache]")
        return 0
    inline = "--inline" in argv
    use_cache = "--no-cache" not in argv
    argv = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    if not argv:
        print("用法: zhihuiya_patent_image_search.py '<JSON 参数>' [--inline] [--no-cache]", file=sys.stderr)
        return 1
    try:
        params = json.loads(argv[0])
    except json.JSONDecodeError as exc:
        print(f"JSON 参数格式无效: {exc}", file=sys.stderr)
        return 1
    if not isinstance(params, dict):
        print("JSON 参数必须为对象", file=sys.stderr)
        return 1
    params["patentType"] = PATENT_TYPE
    model = params.get("model")
    if model is None:
        params["model"] = DEFAULT_MODEL
    elif type(model) is not int or model not in ALLOWED_MODELS:
        print(
            f"本技能仅支持实用新型专利（model 必须为 3 或 4），收到 model={model}；"
            "外观设计专利检索请使用 linkfox-zhihuiya-patent-image-search",
            file=sys.stderr,
        )
        return 1

    try:
        cache_path = _cache_path(params)
    except OSError as exc:
        print(f"当前目录无法创建缓存目录: {exc}", file=sys.stderr)
        return 1
    result = _load_cache(cache_path) if use_cache else None

    def cached_transport(path, request_params):
        if result is not None:
            # 历史缓存可能没有状态；未知不能冒充 HTTP 200，也不为补齐状态重发请求。
            return result.get("_http_status") if isinstance(result, dict) else None, result
        status, body = transport(path, request_params)
        # 业务缓存存储响应 JSON，有效期内复用错误或空结果。
        if use_cache:
            _save_cache(cache_path, response_output(status, body))
        return status, body

    transport = api.call_api
    try:
        run_request(
            API_PATH, "patent-image-search", params,
            inline=inline, transport=cached_transport, cache_path=cache_path,
        )
    except OSError as exc:
        print(f"当前目录无法保存完整响应: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
