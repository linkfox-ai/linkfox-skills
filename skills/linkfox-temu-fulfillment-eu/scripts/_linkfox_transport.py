#!/usr/bin/env python3
"""Temu 认证兼容层：业务请求统一经 call_api.run。"""

import io
import json
import os
import sys
import threading
import time
from contextlib import contextmanager, redirect_stdout
from contextvars import ContextVar
from urllib.parse import urlsplit

import call_api

_LOCK = threading.RLock()
_OUTPUT_PATH = ContextVar("temu_output_path", default=None)


def writable_root():
    """在发送请求前验证 cwd 可写性；不回退其他目录。"""
    root = os.path.abspath(os.path.join(os.getcwd(), "linkfox"))
    os.makedirs(root, exist_ok=True)
    import secrets
    probe = os.path.join(root, ".write-probe-" + secrets.token_hex(6))
    with open(probe, "x", encoding="utf-8"):
        pass
    os.remove(probe)
    return root


@contextmanager
def _overrides(**changes):
    saved = {key: getattr(call_api, key) for key in changes}
    try:
        for key, value in changes.items():
            setattr(call_api, key, value)
        yield
    finally:
        for key, value in saved.items():
            setattr(call_api, key, value)


def take_output_path():
    """业务层解析后覆盖同一响应文件，避免重复落盘或额外缓存。"""
    path = _OUTPUT_PATH.get()
    _OUTPUT_PATH.set(None)
    return path


def request(url, body, token, *, timeout=150):
    """支持显式 Token、双认证头、网关地址别名及 timeout 参数。"""
    _OUTPUT_PATH.set(None)
    root = writable_root()
    slug = "linkfox-temu-fulfillment-eu-" + str(body.get("type") or "file-download").replace(".", "-")
    with _LOCK:
        original_call = call_api.call_api
        original_request = call_api.Request
        original_urlopen = call_api.urlopen
        original_path = call_api._resolve_output_path
        captured = {}

        def gateway_request(*args, **kwargs):
            req = original_request(*args, **kwargs)
            req.add_header("Token", token)
            return req

        def shared_call(api_path, params):
            status, payload = original_call(api_path, params)
            captured["http_status"] = status
            if isinstance(payload, dict):
                payload = dict(payload)
                payload["_http_status"] = status
            captured["payload"] = payload
            # 公共 CLI 的缓存提示读取 .get()；下载 CLI 允许任意 JSON。
            # 仅向公共输出流程提供临时对象，业务返回及最终文件保持原值。
            return status, payload if isinstance(payload, dict) else {"response": payload}

        def output_path(slug, ts):
            # 使用微秒时间戳，为连续请求分别保存响应文件。
            path = original_path(slug, time.time())
            _OUTPUT_PATH.set(path)
            return path

        # 所有 HTTP 的编码、发送和异常处理仍由公共调用器负责。
        # 修改只在本次调用作用域内有效，并在失败时同样恢复。
        with _overrides(
            get_api_key=lambda: token,
            get_api_url=lambda api_path: url,
            Request=gateway_request,
            urlopen=lambda req, timeout=150: original_urlopen(req, timeout=request_timeout),
            call_api=shared_call,
            _linkfox_root=lambda: root,
            _resolve_output_path=output_path,
        ):
            request_timeout = timeout
            with redirect_stdout(io.StringIO()):
                call_api.run(
                    urlsplit(url).path,
                    slug,
                    argv=[json.dumps(body, ensure_ascii=False), "--inline", "--no-cache"],
                )
        if not isinstance(captured["payload"], dict):
            print(f"HTTP status: {captured['http_status']}", file=sys.stderr)
            with open(_OUTPUT_PATH.get(), "w", encoding="utf-8") as stream:
                json.dump(captured["payload"], stream, ensure_ascii=False, indent=2)
        return captured["payload"]
