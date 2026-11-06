#!/usr/bin/env python3
"""美客多选品业务入口，提供 CLI、24 小时缓存和会话输出。

python linkfox_mercado_product_selection.py '<JSON 参数>' [--inline] [--no-cache]
LinkFox HTTP、序列化和输出交给同目录公共调用器；业务缓存仅由本包装维护。
"""

import hashlib
import json
import os
from pathlib import Path
import sys
import time

import call_api as gateway

API_PATH = "/mercado/productSelection"
SLUG = "linkfox-mercado-product-selection"
CACHE_TTL_SEC = 24 * 60 * 60


def _cache_key(params):
    raw = json.dumps(params, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _cache_path(params):
    path = Path.cwd() / "linkfox" / ".cache" / SLUG
    path.mkdir(parents=True, exist_ok=True)
    return str(path / f"{SLUG}-{_cache_key(params)}.json")


def _load_cache(path):
    if not os.path.isfile(path) or time.time() - os.path.getmtime(path) > CACHE_TTL_SEC:
        return None
    try:
        with open(path, encoding="utf-8") as source:
            payload = json.load(source)
        if isinstance(payload, dict):
            payload.setdefault("_cache", {})["hit"] = True
            # 旧缓存没有 HTTP 状态，保持复用但不能将其认作 HTTP 200。
            payload.setdefault("_http_status", None)
        return payload
    except (OSError, json.JSONDecodeError):
        return None


def _save_cache(path, payload):
    try:
        with open(path, "w", encoding="utf-8") as destination:
            json.dump(payload, destination, ensure_ascii=False, indent=2)
    except OSError:
        pass


def _prepare_output_root():
    """会话输出只写 cwd，不使用公共脚本的目录回退。"""
    root = Path.cwd() / "linkfox"
    resolved = root.resolve()
    if resolved == Path("/tmp") or Path("/tmp") in resolved.parents:
        raise OSError("会话数据禁止写入 /tmp，请先切换到可写的项目目录")
    root.mkdir(parents=True, exist_ok=True)
    import tempfile
    with tempfile.TemporaryFile(dir=root):
        pass
    return str(resolved)


def _resolve_output_path(slug, ts):
    """连续调用也各存一份响应，避免公共入口的整秒时间戳覆盖归档。"""
    timestamp_us = max(int(time.time() * 1_000_000), int(ts * 1_000_000))
    while True:
        path = gateway.resolve_data_path(slug, timestamp_us / 1_000_000)
        if not os.path.exists(path):
            return path
        timestamp_us += 1


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if "--help" in args or "-h" in args:
        print("用法：linkfox_mercado_product_selection.py '<JSON 参数>' [--inline] [--no-cache]")
        print('JSON 参数是完整的 {"toolName":"...","arguments":{...}}。')
        return 0
    use_cache = "--no-cache" not in args
    values = [arg for arg in args if arg not in ("--inline", "--no-cache")]
    if not values:
        print("用法：linkfox_mercado_product_selection.py '<JSON 参数>' [--inline] [--no-cache]", file=sys.stderr)
        return 1
    try:
        params = json.loads(values[0])
    except json.JSONDecodeError as exc:
        print(f"参数 JSON 格式错误：{exc}", file=sys.stderr)
        return 1
    try:
        output_root = _prepare_output_root()
        cache_path = _cache_path(params)
    except OSError as exc:
        print(f"当前目录不可写或不允许保存会话数据：{exc}", file=sys.stderr)
        return 1

    # CLI 是单次串行执行。临时适配公共 transport 回调，run 负责唯一一次
    # 输出和归档；finally 恢复模块状态，避免影响同进程的后续调用。
    transport = gateway.call_api
    output_path = gateway._resolve_output_path
    old_root = gateway._SESSION_CACHE.get("_root")

    def cached_transport(api_path, request):
        result = _load_cache(cache_path) if use_cache else None
        if result is not None:
            return result.get("_http_status"), result
        status, result = transport(api_path, request)
        if isinstance(result, dict):
            result = {**result, "_http_status": status}
        if use_cache:
            _save_cache(cache_path, result)
        return status, result

    gateway.call_api = cached_transport
    gateway._resolve_output_path = _resolve_output_path
    gateway._SESSION_CACHE["_root"] = output_root
    try:
        # 业务包装维护缓存，公共调用器禁用缓存以避免重复处理。
        gateway.run(API_PATH, SLUG, [*args, "--no-cache"])
    finally:
        gateway.call_api = transport
        gateway._resolve_output_path = output_path
        if old_root is None:
            gateway._SESSION_CACHE.pop("_root", None)
        else:
            gateway._SESSION_CACHE["_root"] = old_root
    return 0


if __name__ == "__main__":
    sys.exit(main())
