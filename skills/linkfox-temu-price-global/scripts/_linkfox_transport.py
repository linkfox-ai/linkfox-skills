"""Temu 业务兼容层；HTTP、落盘与输出全部交由 call_api.run。"""

from contextlib import contextmanager, redirect_stdout
import io
import json
from pathlib import Path
import sys
import tempfile
import time

import call_api as api

SLUG = "linkfox-temu-price-global"
# 仅保存最近一次 run 的待展示输出，不复用业务响应，也不参与请求缓存。
_pending_output = None


@contextmanager
def _override(name, value):
    previous = getattr(api, name)
    setattr(api, name, value)
    try:
        yield
    finally:
        setattr(api, name, previous)


def call_gateway(url, body, token, timeout=150):
    """使用双头鉴权与自定义基础地址，返回本次请求的对象。"""
    global _pending_output
    _pending_output = None
    root = Path.cwd() / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    # 在发送请求前验证输出目录；禁止公共调用器回退到家目录或临时目录。
    with tempfile.TemporaryFile(dir=root):
        pass

    transport = api.call_api
    request_factory = api.Request
    opener = api.urlopen
    captured = {}

    def request_with_token(*args, **kwargs):
        kwargs["headers"] = {**kwargs.get("headers", {}), "Token": token}
        return request_factory(*args, **kwargs)

    def preserve_timeout(request, **kwargs):
        # 只调整公共 transport 的超时参数，不另行实现或调用其他 HTTP 链路。
        return opener(request, **{**kwargs, "timeout": timeout})

    def process_response(api_path, params):
        status, result = transport(api_path, params)
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

    def output_path(slug, _ts):
        path = api.resolve_data_path(slug, time.time())
        captured["output_path"] = path
        return path

    api_path = "/temu/fileDownload" if url.endswith("/temu/fileDownload") else "/temu/proxy"
    operation = body.get("type", "file-download")
    # 文件标识只用于输出；不让通用代理传入的 type 改变落盘目录。
    operation = "".join(c if c.isalnum() or c in "._-" else "_" for c in str(operation))[:120]
    argv = [json.dumps(body, ensure_ascii=False), "--no-cache"]
    if "--inline" in sys.argv[1:]:
        argv.append("--inline")
    output = io.StringIO()
    with _override("get_api_url", lambda _path: url), \
         _override("get_api_key", lambda: token), \
         _override("Request", request_with_token), \
         _override("urlopen", preserve_timeout), \
         _override("call_api", process_response), \
         _override("_linkfox_root", lambda: str(root)), \
         _override("_resolve_output_path", output_path), \
         redirect_stdout(output):
        api.run(api_path, f"{SLUG}-{operation}", argv=argv)
    result = captured["result"]
    path = captured["output_path"]
    if not Path(path).is_file():
        raise OSError(f"完整响应未保存：{path}\n{output.getvalue()}")
    _pending_output = (result, path)
    return result


def emit_response(result, slug=SLUG, inline=False):
    """响应输出入口，正常请求只展示 run 已经保存的响应。"""
    global _pending_output
    pending = _pending_output
    _pending_output = None
    serialized = json.dumps(result, ensure_ascii=False, indent=2)
    if pending is not None and pending[0] is result:
        path = pending[1]
    else:
        root = Path.cwd() / "linkfox"
        root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryFile(dir=root):
            pass
        with _override("_linkfox_root", lambda: str(root)):
            path = api.resolve_data_path(slug, time.time())
        Path(path).write_text(serialized, encoding="utf-8")
    print(f"Saved full response: {path} ({len(serialized.encode('utf-8'))} bytes)")
    if inline or len(serialized.encode("utf-8")) <= api.SMALL_THRESHOLD:
        print(serialized)
    else:
        api.summarize(result)
