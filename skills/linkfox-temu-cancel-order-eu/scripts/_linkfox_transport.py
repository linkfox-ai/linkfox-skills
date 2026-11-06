"""处理 Temu 认证与输出；HTTP 传输由 call_api.run 执行。"""

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import sys
import tempfile
import time

import call_api as api

SLUG = "linkfox-temu-cancel-order-eu"


def run_gateway(url, body, token, *, timeout=150, display=False):
    """返回原响应并保存一次；业务 CLI 可直接展示公共输出，不启用缓存。"""
    root = Path.cwd() / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    # 在请求之前验证输出位置，不回退到家目录或临时目录。
    with tempfile.TemporaryFile(dir=root):
        pass
    saved = {name: getattr(api, name) for name in (
        "call_api", "get_api_url", "get_api_key", "Request", "urlopen",
        "_resolve_output_path",
    )}
    previous_root = api._SESSION_CACHE.get("_root")
    captured = {}
    transport = saved["call_api"]

    def request(*args, **kwargs):
        headers = dict(kwargs.get("headers") or {})
        headers["Token"] = token
        kwargs["headers"] = headers
        return saved["Request"](*args, **kwargs)

    def open_request(req, **kwargs):
        kwargs["timeout"] = timeout
        return saved["urlopen"](req, **kwargs)

    def with_result(path, params):
        status, result = transport(path, params)
        if isinstance(result, dict):
            result = dict(result)
            result["transportHttpStatus"] = status
            raw = result.get("body")
            if path == "/temu/proxy" and isinstance(raw, str) and raw.strip():
                try:
                    result["temuBody"] = json.loads(raw)
                except json.JSONDecodeError:
                    pass
        else:
            # 公共输出器要求对象；非对象错误响应保留原值供排查。
            result = {"gatewayBody": result, "transportHttpStatus": status}
        captured["result"] = result
        return status, result

    path = "/temu/fileDownload" if url.rstrip("/").endswith("/temu/fileDownload") else "/temu/proxy"
    operation = str(body.get("type") or "file-download")
    # type 由调用方提供；文件名中只保留安全标识，不修改发送内容。
    operation = "".join(c if c.isalnum() or c in "-_." else "_" for c in operation)
    api.call_api = with_result
    api.get_api_url = lambda _path: url
    api.get_api_key = lambda: token
    api.Request = request
    api.urlopen = open_request
    api._SESSION_CACHE["_root"] = str(root)
    api._resolve_output_path = lambda slug, _ts: api.resolve_data_path(slug, time.time())
    argv = [json.dumps(body, ensure_ascii=False), "--no-cache"]
    if "--inline" in sys.argv[1:]:
        argv.append("--inline")
    try:
        if display:
            api.run(path, f"{SLUG}-{operation}", argv=argv)
        else:
            with redirect_stdout(io.StringIO()):
                api.run(path, f"{SLUG}-{operation}", argv=argv)
        return captured["result"]
    finally:
        for name, value in saved.items():
            setattr(api, name, value)
        if previous_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = previous_root
