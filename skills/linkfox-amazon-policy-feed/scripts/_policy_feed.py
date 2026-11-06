#!/usr/bin/env python3
"""政策资讯 CLI 兼容层：限定当前目录落盘，缓存与请求均交给公共调用器。"""

import json
import os
from pathlib import Path
import sys
import tempfile
import time

import call_api


def _prepare_output_root():
    """请求前确认会话目录可写；不使用公共调用器的其他目录回退。"""
    cwd = Path.cwd().resolve()
    if os.name != "nt" and (cwd == Path("/tmp") or Path("/tmp") in cwd.parents):
        raise OSError("禁止在 /tmp 下保存政策资讯，请在项目目录运行")
    sid = (os.environ.get("SESSION_ID") or "").strip()
    if sid and (sid in (".", "..") or "/" in sid or "\\" in sid or os.path.splitdrive(sid)[0]):
        raise ValueError("SESSION_ID 必须是单个会话目录名")
    root = cwd / "linkfox"
    sid = call_api._session_id(time.time())
    directory = root / time.strftime("%Y-%m-%d") / sid / "data"
    directory.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=directory):
        pass
    return str(root)


def run(api_path, slug, argv=None):
    """运行政策资讯 CLI，使用单层 24 小时缓存，列表与全文使用不同缓存标识。"""
    argv = list(sys.argv[1:] if argv is None else argv)
    usage = f"用法：python {Path(sys.argv[0]).name} '<JSON 参数>' [--inline] [--no-cache]"
    if argv in (["--help"], ["-h"]):
        print(usage)
        return 0
    positional = [a for a in argv if a not in ("--inline", "--no-cache")]
    if len(positional) != 1:
        print(usage, file=sys.stderr)
        return 1
    try:
        params = json.loads(positional[0])
        if not isinstance(params, dict):
            raise ValueError("JSON 参数必须为 object")
    except ValueError as exc:
        print(f"参数错误：{exc}", file=sys.stderr)
        return 1

    # 兼容空白会话变量，并在本次调用结束后恢复进程状态。
    previous_sid = os.environ.get("SESSION_ID")
    previous_root = call_api._SESSION_CACHE.get("_root")
    previous_output_path = call_api._resolve_output_path
    previous_load_cache = call_api._load_cache

    def load_valid_cache(path):
        """读取公共调用器缓存；损坏的缓存视为未命中，仅使用一层响应缓存。"""
        try:
            payload = previous_load_cache(path)
        except (TypeError, AttributeError, KeyError, UnicodeError):
            return None
        return payload if call_api._is_cacheable(200, payload) else None

    try:
        if previous_sid is not None and not previous_sid.strip():
            os.environ.pop("SESSION_ID", None)
        try:
            root = _prepare_output_root()
        except (ValueError, OSError) as exc:
            print(f"输出目录错误：{exc}", file=sys.stderr)
            return 1
        # 指定当前目录落盘与有效缓存读取方式，HTTP 请求由公共调用器的 run 处理。
        call_api._SESSION_CACHE["_root"] = root
        call_api._resolve_output_path = lambda slug, _ts: call_api.resolve_data_path(slug, time.time())
        call_api._load_cache = load_valid_cache
        call_api.run(api_path, f"{slug}-{api_path.rsplit('/', 1)[-1]}", argv)
    finally:
        call_api._resolve_output_path = previous_output_path
        call_api._load_cache = previous_load_cache
        if previous_sid is not None:
            os.environ["SESSION_ID"] = previous_sid
        if previous_root is None:
            call_api._SESSION_CACHE.pop("_root", None)
        else:
            call_api._SESSION_CACHE["_root"] = previous_root
    return 0
