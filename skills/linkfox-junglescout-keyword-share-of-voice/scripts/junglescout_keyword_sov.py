#!/usr/bin/env python3
"""Jungle Scout 关键词声量：提供业务缓存，通过公共调用器请求并落盘。

用法：python junglescout_keyword_sov.py '<JSON 参数>' [--inline] [--no-cache]
默认启用 24 小时缓存；--inline 强制全量打印，--no-cache 禁用缓存。
"""

import hashlib
import json
import os
import sys
import time
import call_api as _common

API_PATH = "/tool-jungle-scout/keywords/share-of-voice"
SLUG = "linkfox-junglescout-keyword-share-of-voice"
CACHE_TTL_SEC = 24 * 60 * 60

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8")
        except (OSError, ValueError):
            pass


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


def _linkfox_root():
    """响应写入当前工作目录，不使用公共调用器的目录回退。"""
    root = os.path.abspath(os.path.join(os.getcwd(), "linkfox"))
    os.makedirs(root, exist_ok=True)
    # 使用独立探测文件，避免覆盖现有文件。
    import tempfile
    with tempfile.TemporaryFile(dir=root):
        pass
    return root


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--help" in argv or "-h" in argv:
        print(__doc__)
        return
    # 缺参及无效 JSON 由公共调用器返回本地错误，不触发请求。
    args = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    if not args:
        return _common.run(API_PATH, SLUG, argv=argv + ["--no-cache"])
    try:
        json.loads(args[0])
    except json.JSONDecodeError:
        return _common.run(API_PATH, SLUG, argv=argv + ["--no-cache"])
    try:
        _linkfox_root()
    except OSError as exc:
        print(f"当前工作目录不可写，未发送请求：{exc}", file=sys.stderr)
        raise SystemExit(1)

    use_cache = "--no-cache" not in argv
    transport = _common.call_api
    root_resolver = _common._linkfox_root

    def cached_transport(api_path, params):
        cache_path = _cache_path(params) if use_cache else None
        result = _load_cache(cache_path) if use_cache else None
        if result is None:
            result = transport(api_path, params)
            if use_cache:
                _save_cache(cache_path, result)
        return result

    # 业务层管理缓存；请求、输出与会话元数据交给公共 run。
    _common.call_api = cached_transport
    _common._linkfox_root = _linkfox_root
    try:
        return _common.run(API_PATH, SLUG, argv=argv + ["--no-cache"])
    finally:
        _common.call_api = transport
        _common._linkfox_root = root_resolver


if __name__ == "__main__":
    main()
