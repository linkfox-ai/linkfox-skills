#!/usr/bin/env python3
"""店铺接口的业务缓存与输出兼容；LinkFox HTTP 由公共调用器负责。"""

from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import sys
import time

import call_api

SLUG = "linkfox-kalodata-tiktok-shop"
CACHE_TTL_SEC = 24 * 60 * 60


def _cache_key(params):
    raw = json.dumps(params, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _cache_path(operation, params):
    root = Path.cwd() / "linkfox" / ".cache" / SLUG
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{SLUG}-{operation}-{_cache_key(params)}.json"


def _load_cache(path):
    try:
        if not path.is_file() or time.time() - path.stat().st_mtime > CACHE_TTL_SEC:
            return None
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or not isinstance(payload.get("_cache", {}), dict):
            return None
        payload.setdefault("_cache", {})["hit"] = True
        # 旧缓存未记录 HTTP 状态，保留未知值，不把缓存命中解释为 HTTP 200。
        payload.setdefault("_http_status", None)
        return payload
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None


def _save_cache(path, payload):
    # 缓存包含空响应与业务错误；明确重试使用 --no-cache。
    try:
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        pass


def _working_root():
    """数据写入当前工作目录，不采用公共调用器的目录回退。"""
    root = Path.cwd() / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    probe = root / f".kalodata-write-probe-{os.getpid()}-{time.time_ns()}"
    with probe.open("x", encoding="utf-8"):
        pass
    probe.unlink()
    return str(root)


@contextmanager
def _caller_hooks(**hooks):
    """单次同步 CLI 的业务适配；离开调用后恢复公共模块，不修改其源文件。"""
    original = {name: getattr(call_api, name) for name in hooks}
    try:
        for name, value in hooks.items():
            setattr(call_api, name, value)
        yield
    finally:
        for name, value in original.items():
            setattr(call_api, name, value)


def main(api_path, argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    inline = "--inline" in argv
    use_cache = "--no-cache" not in argv
    positional = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    if not positional:
        print(f"用法：{Path(sys.argv[0]).name} '<JSON 参数>' [--inline] [--no-cache]", file=sys.stderr)
        return 1
    try:
        params = json.loads(positional[0])
    except json.JSONDecodeError as exc:
        print(f"JSON 参数格式无效：{exc}", file=sys.stderr)
        return 1
    if not isinstance(params, dict):
        print("JSON 参数必须为对象", file=sys.stderr)
        return 1

    operation = api_path.rsplit("/", 1)[-1]
    try:
        # 在任何可能收费的请求前检查落盘目录。
        root = _working_root()
        cache_path = _cache_path(operation, params)
        result = _load_cache(cache_path) if use_cache else None
        transport = call_api.call_api

        def business_transport(path, body):
            nonlocal result
            if result is not None:
                print(f"Cached HTTP status: {result['_http_status']}", file=sys.stderr)
                return result["_http_status"], result
            status, payload = transport(path, body)
            payload = dict(payload)
            payload["_http_status"] = status
            # 公共输出仅展示响应体；单独显示状态，确保大响应摘要也不丢失。
            print(f"HTTP status: {status}", file=sys.stderr)
            result = payload
            if use_cache:
                _save_cache(cache_path, payload)
            return status, payload

        def prepare_output_path():
            # 公共 run 的 ts 精度为秒；业务封装保留微秒，防止同秒覆盖。
            stamp = time.time()
            _, session_dir = call_api._ensure_session(stamp)
            data_dir = Path(session_dir) / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            out = data_dir / f"{SLUG}-{operation}-{time.time_ns() // 1000}.json"
            # 验证实际会话目录和文件的写入能力，失败时不得先发起收费请求。
            with out.open("x", encoding="utf-8"):
                pass
            out.unlink()
            call_api._update_meta(
                session_dir, skill=SLUG, kind="data",
                file_rel=os.path.relpath(out, session_dir), ts=stamp,
            )
            return str(out)

        hooks = {
            "call_api": business_transport,
            "_linkfox_root": lambda: root,
            "_cache_path": lambda slug, body: str(cache_path),
        }
        args = [json.dumps(params, ensure_ascii=False), "--no-cache"]
        if inline:
            args.append("--inline")
        with _caller_hooks(**hooks):
            out_path = prepare_output_path()
            with _caller_hooks(_resolve_output_path=lambda slug, ts: out_path):
                call_api.run(api_path, SLUG, argv=args)
            # 公共调用器会打印保存错误但不改变退出码，由业务封装补充失败状态。
            saved = Path(out_path).read_text(encoding="utf-8")
            if saved != json.dumps(result, ensure_ascii=False, indent=2):
                print("完整响应未保存，当前调用执行失败", file=sys.stderr)
                return 1
        return 0
    except (OSError, UnicodeError) as exc:
        print(f"当前目录数据保存失败：{exc}", file=sys.stderr)
        return 1
