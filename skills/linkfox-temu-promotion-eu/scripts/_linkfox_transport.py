#!/usr/bin/env python3
"""Temu 认证、解析和输出兼容层；HTTP、落盘和 CLI 均委托公共调用器。"""

import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import threading
import time
from urllib.parse import urlsplit

import call_api as api

SLUG = "linkfox-temu-promotion-eu"
_LOCK = threading.RLock()
_LAST_OUTPUT = None


def run_temu_api(url, body, linkfox_token, timeout=150):
    """支持 JSON 密钥、双鉴权头与自定义网关；响应缓存关闭，HTTP 由公共调用器处理。"""
    global _LAST_OUTPUT
    root = Path.cwd() / "linkfox"
    if sys.platform != "win32" and Path("/tmp") in root.resolve().parents:
        raise OSError("本技能禁止将业务响应保存到 /tmp。")
    root.mkdir(parents=True, exist_ok=True)
    # 在请求之前检查写权限，不使用公共调用器的家目录或临时目录回退。
    with tempfile.TemporaryFile(dir=root):
        pass

    api_path = urlsplit(url).path
    operation = str(body.get("type") or "file-download").replace(".", "-")
    slug = f"{SLUG}-{operation}"
    with _LOCK:
        _LAST_OUTPUT = None
        originals = {name: getattr(api, name) for name in (
            "call_api", "get_api_key", "get_api_url", "Request", "urlopen", "_resolve_output_path"
        )}
        previous_root = api._SESSION_CACHE.get("_root")
        collected = {}

        def request_with_token(*args, **kwargs):
            request = originals["Request"](*args, **kwargs)
            request.add_header("Token", linkfox_token)
            return request

        def open_with_timeout(request, timeout=150):
            # 将业务函数的 timeout 参数传给公共 transport，不自行构造 HTTP 请求。
            return originals["urlopen"](request, timeout=timeout_value)

        def parse_transport(path, params):
            status, result = originals["call_api"](path, params)
            if not isinstance(result, dict):
                result = {"gatewayBody": result, "error": "网关响应不是 JSON 对象"}
            result["transportHttpStatus"] = status
            raw = result.get("body")
            if isinstance(raw, str) and raw.strip():
                try:
                    result["temuBody"] = json.loads(raw)
                except json.JSONDecodeError:
                    pass
            collected["result"] = result
            return status, result

        def unique_output_path(output_slug, _ts):
            return api.resolve_data_path(output_slug, time.time())

        timeout_value = timeout
        api.call_api = parse_transport
        api.get_api_key = lambda: linkfox_token
        api.get_api_url = lambda _path: url
        api.Request = request_with_token
        api.urlopen = open_with_timeout
        api._resolve_output_path = unique_output_path
        api._SESSION_CACHE["_root"] = str(root)
        argv = [json.dumps(body, ensure_ascii=False), "--no-cache"]
        if "--inline" in sys.argv[1:]:
            argv.append("--inline")
        output = io.StringIO()
        try:
            with contextlib.redirect_stdout(output):
                api.run(api_path, slug, argv=argv)
            result = collected["result"]
            _LAST_OUTPUT = (result, output.getvalue())
            return result
        finally:
            for name, value in originals.items():
                setattr(api, name, value)
            if previous_root is None:
                api._SESSION_CACHE.pop("_root", None)
            else:
                api._SESSION_CACHE["_root"] = previous_root


def emit_result(result, slug=SLUG, inline=False):
    """业务入口复用 run 已保存的响应与输出，不二次落盘。"""
    global _LAST_OUTPUT
    record = _LAST_OUTPUT
    if record is not None and record[0] is result:
        _LAST_OUTPUT = None
        if inline and "--inline" not in sys.argv[1:]:
            print(record[1].splitlines()[0])
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(record[1], end="")
        return
    # emit_result 支持本地加工结果；此分支仅落盘与打印，不进行网络调用。
    root = Path.cwd() / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    if sys.platform != "win32" and Path("/tmp") in root.resolve().parents:
        raise OSError("本技能禁止将业务响应保存到 /tmp。")
    previous_root = api._SESSION_CACHE.get("_root")
    api._SESSION_CACHE["_root"] = str(root)
    try:
        out = api.resolve_data_path(slug, time.time())
        serialized = json.dumps(result, ensure_ascii=False, indent=2)
        Path(out).write_text(serialized, encoding="utf-8")
        print(f"Saved full response: {out} ({len(serialized.encode('utf-8'))} bytes)")
        if inline or len(serialized.encode("utf-8")) <= api.SMALL_THRESHOLD:
            print(serialized)
        else:
            api.summarize(result)
    finally:
        if previous_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = previous_root
