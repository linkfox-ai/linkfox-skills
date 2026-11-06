#!/usr/bin/env python3
"""视频业务封装：提供身份隔离缓存和 CLI，HTTP 与落盘使用公共调用器。"""

import hashlib
import io
import json
import os
from pathlib import Path
import sys
import time
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

import call_api


SLUG = "linkfox-chuhaijiang-tiktok-video"
CACHE_TTL_SEC = 24 * 60 * 60


def _cache_key(api_path, params):
    """缓存键按网关、端点、密钥指纹和参数生成；密钥不落盘明文。"""
    raw = json.dumps(
        {
            "version": 1,
            "apiBase": call_api.get_api_base(),
            "apiPath": api_path,
            "apiKeyFingerprint": hashlib.sha256(
                call_api.get_api_key().encode("utf-8")
            ).hexdigest(),
            "params": params,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]


def _cache_path(api_path, params):
    root = Path.cwd() / "linkfox" / ".cache" / SLUG
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{SLUG}-{_cache_key(api_path, params)}.json"


def _cacheable(status, payload):
    """根据 HTTP 状态、基本响应规则与业务失败标记判断是否可缓存。"""
    if type(status) is not int or not 200 <= status < 300:
        return False
    if not isinstance(payload, dict) or payload.get("error") or payload.get("success") is False:
        return False
    # 公共实现的 errcode 判断与基础规则一致；传入 200 仅复用该判断，
    # 上面的真实状态检查覆盖全部 2xx 状态。
    if not call_api._is_cacheable(200, payload):
        return False
    for key in ("code", "errorCode"):
        if key in payload and str(payload[key]).lower() not in ("0", "200", "ok", "success"):
            return False
    return True


def _load_cache(path):
    try:
        if time.time() - path.stat().st_mtime > CACHE_TTL_SEC:
            return None
        result = json.loads(path.read_text(encoding="utf-8"))
        # 缓存直接保存响应体；读取时重新检查可缓存性，排除 errcode=0。
        return result if _cacheable(200, result) else None
    except (OSError, ValueError):
        return None


def _save_cache(path, payload):
    try:
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        # 缓存写入失败不丢弃已取得的响应。
        pass


def _strict_root():
    """仅在当前工作目录落盘，不使用公共调用器的目录回退。"""
    root = Path.cwd() / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    probe = root / ".write_probe"
    probe.write_text("", encoding="utf-8")
    probe.unlink()
    return str(root)


def run(api_path, argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if "--help" in args or "-h" in args:
        print(f"用法：{Path(sys.argv[0]).name} '<JSON 参数>' [--inline] [--no-cache]")
        return 0
    use_cache = "--no-cache" not in args
    inline = "--inline" in args
    positional = [arg for arg in args if arg not in ("--inline", "--no-cache")]
    if not positional:
        print(f"用法：{Path(sys.argv[0]).name} '<JSON 参数>' [--inline] [--no-cache]", file=sys.stderr)
        return 1
    try:
        params = json.loads(positional[0])
        if not isinstance(params, dict):
            raise ValueError("JSON 参数必须是对象")
    except ValueError as exc:
        print(f"参数格式无效：{exc}", file=sys.stderr)
        return 1

    # 在付费请求前验证身份与当前目录；预留微秒级输出文件防止连续调用覆盖。
    call_api.get_api_key()
    sid = (os.environ.get("SESSION_ID") or "").strip()
    try:
        with patch.object(call_api, "_linkfox_root", _strict_root), \
             patch.dict(os.environ, {"SESSION_ID": sid}):
            output_path = call_api.resolve_data_path(SLUG, time.time())
        Path(output_path).write_text("", encoding="utf-8")
        cache_path = _cache_path(api_path, params) if use_cache else None
    except OSError as exc:
        print(f"无法保存完整响应：{exc}", file=sys.stderr)
        return 1

    transport = call_api.call_api
    summarize = call_api.summarize
    cache_hit = False
    result_size = 0

    def cached_transport(path, request):
        nonlocal cache_hit, result_size
        result = _load_cache(cache_path) if cache_path else None
        if result is not None:
            cache_hit = True
            status = 200
        else:
            try:
                status, result = transport(path, request)
            except (OSError, ValueError) as exc:
                status, result = None, {"error": f"请求失败：{exc}"}
            if cache_path and _cacheable(status, result):
                _save_cache(cache_path, result)
        if not isinstance(result, dict):
            result = {"error": "接口响应不是 JSON 对象", "details": result}
        result_size = len(json.dumps(result, ensure_ascii=False, indent=2).encode("utf-8"))
        return status, result

    def business_summary(result):
        data = result.get("data")
        if isinstance(data, dict) and "total_count" in data:
            print(f"  data.total_count: {data['total_count']}")
        summarize(result)

    # 公共 run 没有 transport/output 注入参数；仅在同步 CLI 执行期间
    # 适配缓存入口、预留文件及摘要，退出（包括异常）后还原函数绑定。
    # 不实现 HTTP，不修改公共文件，也不启用公共调用器的第二层缓存。
    capture = io.StringIO()
    errors = io.StringIO()
    try:
        with patch.object(call_api, "call_api", cached_transport), \
             patch.object(call_api, "_resolve_output_path", lambda *_: output_path), \
             patch.object(call_api, "_cache_path", lambda *_: ""), \
             patch.object(call_api, "summarize", business_summary), \
             patch.dict(os.environ, {"SESSION_ID": sid}), \
             redirect_stdout(capture), redirect_stderr(errors):
            call_api.run(api_path, SLUG, [json.dumps(params, ensure_ascii=False),
                                        *(["--inline"] if inline else []), "--no-cache"])
        output = capture.getvalue()
        error_output = errors.getvalue()
        # 公共调用器将落盘失败写入 stderr 并继续返回，业务入口以非零状态退出。
        if any(line.startswith("Failed to save to ") for line in error_output.splitlines()):
            raise OSError(error_output.strip())
        # 落盘提示使用响应序列化后的 UTF-8 字节数。
        lines = output.splitlines(keepends=True)
        if lines and lines[0].startswith("Saved full response: "):
            lines[0] = f"Saved full response: {output_path} ({result_size} bytes)\n"
            if cache_hit:
                lines.insert(1, f"Cache hit: {cache_path}\n")
        print("".join(lines), end="")
        print(error_output, end="", file=sys.stderr)
        if cache_hit:
            if inline or result_size <= call_api.SMALL_THRESHOLD:
                print(f"Cache hit: {cache_path}", file=sys.stderr)
        return 0
    except OSError as exc:
        print(f"无法保存完整响应：{exc}", file=sys.stderr)
        return 1
