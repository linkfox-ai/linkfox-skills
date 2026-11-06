"""直播入口的本地运行约定；HTTP、缓存与响应输出由公共调用器负责。"""

import json
import os
from pathlib import Path
import sys
import tempfile
import time

import call_api


def _load_valid_cache(path):
    """读取公共缓存格式；损坏、过期或非正常响应一律视为未命中。"""
    try:
        if time.time() - os.path.getmtime(path) > call_api.CACHE_TTL_SEC:
            return None
        with open(path, encoding="utf-8") as stream:
            cached = json.load(stream)
        if not isinstance(cached, dict) or type(cached.get("_cache_version")) is not int:
            return None
        if cached["_cache_version"] != 1:
            return None
        payload = cached.get("body")
        if not call_api._is_cacheable(cached.get("http_status"), payload):
            return None
        payload["_cache"] = {"hit": True}
        return payload
    except (OSError, ValueError):
        return None


def _resolve_output_path(slug, ts):
    """公共流程传入整秒时间；使用高精度时间避免同秒响应互相覆盖。"""
    return call_api.resolve_data_path(slug, time.time_ns() / 1_000_000_000)


def run_livestream(api_path, slug, argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    # 参数错误由公共 CLI 处理，不创建运行目录。
    params_args = [arg for arg in args if arg not in ("--inline", "--no-cache")]
    if not params_args:
        return call_api.run(api_path, slug, args)
    try:
        params = json.loads(params_args[0])
    except json.JSONDecodeError:
        return call_api.run(api_path, slug, args)
    if not isinstance(params, dict):
        print("JSON 参数必须为对象", file=sys.stderr)
        raise SystemExit(1)

    # 固定到当前目录；不能因不可写而在其他目录落盘。
    cwd = Path.cwd().resolve()
    if cwd == Path("/tmp").resolve() or Path("/tmp").resolve() in cwd.parents:
        print("禁止在 /tmp 下运行，请切换到可写的项目目录", file=sys.stderr)
        raise SystemExit(1)
    root = cwd / "linkfox"
    try:
        root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryFile(dir=root):
            pass
    except OSError as exc:
        print(f"当前目录无法保存完整响应：{exc}", file=sys.stderr)
        raise SystemExit(1)

    previous = call_api._SESSION_CACHE.get("_root")
    previous_load = call_api._load_cache
    previous_output = call_api._resolve_output_path
    previous_call = call_api.call_api

    def call_with_http_status(path, request_params):
        http_status, payload = previous_call(path, request_params)
        # 错误 JSON 未必包含状态码；保留 HTTP 分流依据及完整响应原文。
        if http_status is not None and not 200 <= http_status < 300:
            print(f"HTTP status: {http_status}", file=sys.stderr)
        return http_status, payload

    call_api._SESSION_CACHE["_root"] = os.fspath(root)
    # 复用公共调用器的一层缓存与完整 CLI，业务钩子补充运行约定。
    call_api._load_cache = _load_valid_cache
    call_api._resolve_output_path = _resolve_output_path
    call_api.call_api = call_with_http_status
    try:
        return call_api.run(api_path, slug, args)
    finally:
        call_api._load_cache = previous_load
        call_api._resolve_output_path = previous_output
        call_api.call_api = previous_call
        if previous is None:
            call_api._SESSION_CACHE.pop("_root", None)
        else:
            call_api._SESSION_CACHE["_root"] = previous
