"""Temu 业务兼容层：统一 run，无响应缓存，不重复落盘。"""
from __future__ import annotations

import io
import json
import os
import sys
import tempfile
import time
from contextlib import redirect_stdout
from pathlib import Path

import call_api as api

SLUG = "linkfox-temu-price-eu"
_pending = None


def gateway_call(url: str, body: dict, token: str, timeout: int = 150) -> dict:
    """复用公共 transport，发送 Token 头并返回网关响应。"""
    global _pending
    # 请求前检查当前目录可写；不允许公共调用器回退到家目录或临时目录。
    root = Path.cwd() / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    base, path = url.rsplit("/temu/", 1)
    api_path = "/temu/" + path
    old_env = {k: os.environ.get(k) for k in ("LINKFOX_TOOL_GATEWAY", "LINKFOX_AGENT_API_KEY", "ACPX_WORKSPACES")}
    old_root = api._SESSION_CACHE.get("_root")
    transport, request_factory, output_path = api.call_api, api.Request, api._resolve_output_path
    open_url = api.urlopen
    captured = {}

    def request_with_token(*args, **kwargs):
        request = request_factory(*args, **kwargs)
        request.add_header("Token", token)
        return request

    def with_timeout(request, **kwargs):
        # 默认超时为 150 秒，也接受业务 helper 显式传入的 timeout。
        return open_url(request, **{**kwargs, "timeout": timeout})

    def with_temu_body(endpoint, params):
        status, result = transport(endpoint, params)
        if not isinstance(result, dict):
            result = {"body": result}
        result["transportHttpStatus"] = status
        raw = result.get("body")
        if api_path == "/temu/proxy" and isinstance(raw, str) and raw.strip():
            try:
                result["temuBody"] = json.loads(raw)
            except json.JSONDecodeError:
                pass
        captured["result"] = result
        return status, result

    os.environ.update(LINKFOX_TOOL_GATEWAY=base, LINKFOX_AGENT_API_KEY=token, ACPX_WORKSPACES=str(Path.cwd()))
    api._SESSION_CACHE["_root"] = str(root)
    api.Request = request_with_token
    api.urlopen = with_timeout
    api.call_api = with_temu_body
    api._resolve_output_path = lambda slug, ts: api.resolve_data_path(slug, time.time())
    stream = io.StringIO()
    _pending = None
    try:
        argv = [json.dumps(body, ensure_ascii=False), "--no-cache"]
        if "--inline" in sys.argv:
            argv.append("--inline")
        # run 已保存并格式化结果，暂存输出，供先返回结果、再 emit_result 的调用链使用。
        with redirect_stdout(stream):
            api.run(api_path, SLUG, argv=argv)
        result = captured["result"]
        _pending = (result, stream.getvalue())
        return result
    finally:
        api.call_api, api.Request, api._resolve_output_path = transport, request_factory, output_path
        api.urlopen = open_url
        if old_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = old_root
        for key, value in old_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def emit_result(result, slug=SLUG, inline=False):
    """输出 run 已保存的响应；不进行第二次保存或任何缓存。"""
    global _pending
    if _pending is None or _pending[0] is not result:
        raise RuntimeError("emit_result 必须接收本次 gateway_call 返回的对象")
    rendered = _pending[1]
    _pending = None
    print(rendered, end="")
