#!/usr/bin/env python3
"""Temu 兼容层：通过公共 run 完成鉴权、无缓存调用与业务输出。"""

import io
import json
import tempfile
import time
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import call_api

SLUG = "linkfox-temu-returns-refunds-us"
_RESULT_FILES = {}


def strict_output_root():
    """请求前验证 cwd 可写，禁止公共调用器回退其他目录。"""
    root = Path.cwd() / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    return str(root.resolve())


def request_via_run(url, body, token, timeout=150):
    """不实现 HTTP：为公共调用器提供 Temu 请求头及网关基础地址兼容。"""
    root = strict_output_root()
    marker = "/temu/"
    base, found, suffix = url.rpartition(marker)
    if not found:
        raise ValueError("Temu 请求地址必须包含 /temu/")
    api_path = marker + suffix
    original_call = call_api.call_api
    original_request = call_api.Request
    original_urlopen = call_api.urlopen
    captured = {}

    def request_with_token(*args, **kwargs):
        request = original_request(*args, **kwargs)
        request.add_header("Token", token)
        return request

    def open_with_timeout(request, **kwargs):
        kwargs["timeout"] = timeout
        return original_urlopen(request, **kwargs)

    def capture_response(path, params):
        # 先验证真正的会话数据目录；根目录可写不代表其已有子目录可写。
        saved_path = call_api.resolve_data_path(SLUG, time.time())
        with tempfile.TemporaryFile(dir=Path(saved_path).parent):
            pass
        captured["path"] = saved_path
        status, result = original_call(path, params)
        if isinstance(result, dict):
            # 以实际 transport 为准，不接受响应体同名字段覆盖 HTTP 状态。
            result["transportHttpStatus"] = status
        captured["result"] = result
        return status, result

    def output_path(slug, _timestamp):
        # 复用请求前准备的微秒文件名，避免重复落盘及连续调用覆盖。
        return captured["path"]

    with patch.object(call_api, "get_api_base", lambda: base.rstrip("/")), \
         patch.object(call_api, "get_api_key", lambda: token), \
         patch.object(call_api, "Request", request_with_token), \
         patch.object(call_api, "urlopen", open_with_timeout), \
         patch.object(call_api, "call_api", capture_response), \
         patch.object(call_api, "_linkfox_root", lambda: root), \
         patch.object(call_api, "_resolve_output_path", output_path), \
         redirect_stdout(io.StringIO()):
        call_api.run(api_path, SLUG, [json.dumps(body, ensure_ascii=False), "--no-cache"])
    result = captured["result"]
    _RESULT_FILES[id(result)] = (result, captured["path"])
    return result


def take_saved_path(result):
    saved = _RESULT_FILES.pop(id(result), None)
    if saved and saved[0] is result:
        return saved[1]
    return None
