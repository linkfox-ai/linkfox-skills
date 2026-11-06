"""Temu 兼容层：复用公共调用器，保留认证头、超时和已有函数返回值。"""

from contextlib import ExitStack, redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys
import tempfile
import time
from unittest.mock import patch
from urllib.parse import urlsplit

import call_api as api

SLUG = "linkfox-temu-order-us"
_last_output = None
_last_response = None


def cwd_root():
    """请求前验证当前目录，不采用公共调用器的家目录/临时目录回退。"""
    root = Path.cwd() / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    return str(root)


def call(url, body, *, headers, timeout=150):
    """HTTP 由公共 call_api 执行；捕获输出供 emit_result 重放。"""
    global _last_output, _last_response
    _last_output = None
    _last_response = None
    root = cwd_root()
    captured = {}
    transport = api.call_api
    request_factory = api.Request
    opener = api.urlopen
    api_path = urlsplit(url).path
    is_proxy = api_path.endswith("/temu/proxy")

    def compatible_request(*args, **kwargs):
        kwargs["headers"] = {**kwargs.get("headers", {}), **headers}
        return request_factory(*args, **kwargs)

    def compatible_open(request, timeout=150):
        return opener(request, timeout=actual_timeout)

    actual_timeout = timeout

    def with_temu_body(path, params):
        status, result = transport(path, params)
        captured["status"] = status
        print(f"Gateway HTTP status: {status}", file=sys.stderr)
        if is_proxy and isinstance(result, dict):
            raw = result.get("body")
            if isinstance(raw, str) and raw.strip():
                try:
                    result["temuBody"] = json.loads(raw)
                except json.JSONDecodeError:
                    pass
        captured["result"] = result
        # 公共 run 以对象为入口；非对象 JSON 完整保留，调用函数返回原始值。
        return status, result if isinstance(result, dict) else {"gatewayResponse": result}

    operation = str(body.get("type") or "fileDownload")
    # type 在 US 通用入口可任意提供，文件名只保留安全字符。
    operation = "".join(c if c.isascii() and (c.isalnum() or c in "-_.") else "_" for c in operation)[:96]
    slug = f"{SLUG}-{operation}"
    argv = [json.dumps(body, ensure_ascii=False), "--no-cache"]
    if "--inline" in sys.argv[1:]:
        argv.append("--inline")
    output = StringIO()
    # 所有覆盖仅限同步调用期间，结束后恢复公共模块，不改公共调用器文件。
    with ExitStack() as stack:
        for name, value in {
            "get_api_url": lambda _path: url,
            "get_api_key": lambda: headers["Authorization"],
            "Request": compatible_request,
            "urlopen": compatible_open,
            "call_api": with_temu_body,
            "_linkfox_root": lambda: root,
            "_resolve_output_path": lambda name, _ts: api.resolve_data_path(name, time.time()),
        }.items():
            stack.enter_context(patch.object(api, name, value))
        stack.enter_context(redirect_stdout(output))
        api.run(api_path, slug, argv=argv)
    result = captured["result"]
    _last_response = (result, captured["status"])
    _last_output = (result, output.getvalue())
    return result


def http_status(result):
    """返回同次调用的外层 HTTP 状态，不向网关响应注入同名业务字段。"""
    if _last_response is not None and _last_response[0] is result:
        return _last_response[1]
    return None


def replay(result):
    """CLI 调用 emit_result 时重放输出；只打印一次并只保存同一份结果。"""
    global _last_output
    if _last_output is None or _last_output[0] is not result:
        return False
    print(_last_output[1], end="")
    _last_output = None
    return True
