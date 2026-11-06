"""通过公共 run 保留 Temu 双头鉴权、超时与业务输出，不启用响应缓存。"""

import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import threading
import time
from urllib.error import HTTPError

import call_api as api

_LOCK = threading.RLock()
SLUG = "linkfox-temu-compliance-global"


class GatewayResult(dict):
    """以 dict 返回响应，并延迟展示公共调用器已经保存的响应。"""

    rendered_output = ""
    rendered_inline = False


def call_gateway(url, body, token, timeout=150):
    """所有网络请求由公共调用器发出；本层适配业务脚本的调用与返回格式。"""
    with _LOCK:
        root = Path.cwd() / "linkfox"
        root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryFile(dir=root):
            pass
        previous = {name: getattr(api, name) for name in (
            "call_api", "get_api_url", "get_api_key", "Request", "urlopen",
            "_resolve_output_path",
        )}
        previous_root = api._SESSION_CACHE.get("_root")
        captured = {}

        def request_with_token(*args, **kwargs):
            kwargs["headers"] = dict(kwargs.get("headers") or {}, Token=token)
            return previous["Request"](*args, **kwargs)

        def with_temu_body(path, params):
            status, payload = previous["call_api"](path, params)
            if isinstance(payload, dict):
                # 本地传输状态随完整响应落盘，供 HTTP 401/402 等分支判断。
                payload["_http_status"] = status
            if captured.get("empty_http_error") and isinstance(payload, dict):
                # 空 HTTP 错误体也返回 details 空字符串。
                payload.setdefault("details", "")
            if isinstance(payload, dict) and url.rstrip("/").endswith("/temu/proxy"):
                raw = payload.get("body")
                if isinstance(raw, str) and raw.strip():
                    try:
                        payload["temuBody"] = json.loads(raw)
                    except json.JSONDecodeError:
                        pass
            captured["payload"] = payload
            return status, payload

        def with_timeout(request, **kwargs):
            try:
                return previous["urlopen"](request, timeout=timeout)
            except HTTPError as error:
                # 只记录错误体是否为空；仍由公共调用器解析 HTTP 错误。
                raw = error.read() if error.fp else b""
                captured["empty_http_error"] = not raw
                raise HTTPError(error.url, error.code, error.reason,
                                error.headers, io.BytesIO(raw)) from error

        api.get_api_url = lambda path: url
        api.get_api_key = lambda: token
        api.Request = request_with_token
        # 通过公共调用器持有的 transport 使用业务入口传入的 timeout。
        api.urlopen = with_timeout
        api.call_api = with_temu_body
        api._SESSION_CACHE["_root"] = str(root)
        output = io.StringIO()
        errors = io.StringIO()
        try:
            # 请求前检查实际会话 data 目录，避免请求已完成才发现结果无法保存。
            output_path = api.resolve_data_path(SLUG, time.time())
            with tempfile.TemporaryFile(dir=Path(output_path).parent):
                pass
            api._resolve_output_path = lambda slug, ts: output_path
            argv = [json.dumps(body, ensure_ascii=False), "--no-cache"]
            inline = "--inline" in sys.argv[1:]
            if inline:
                argv.append("--inline")
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
                api.run("/temu/fileDownload" if url.endswith("/temu/fileDownload") else "/temu/proxy", SLUG, argv=argv)
            if "Failed to save to " in errors.getvalue():
                raise OSError(errors.getvalue().strip())
            if errors.getvalue():
                print(errors.getvalue(), file=sys.stderr, end="")
        finally:
            for name, value in previous.items():
                setattr(api, name, value)
            if previous_root is None:
                api._SESSION_CACHE.pop("_root", None)
            else:
                api._SESSION_CACHE["_root"] = previous_root
        result = GatewayResult(captured["payload"])
        result.rendered_output = output.getvalue()
        result.rendered_inline = inline
        return result


def emit_result(result, slug=SLUG, inline=False):
    """业务入口通过 emit_result 展示一次已落盘响应。"""
    if isinstance(result, GatewayResult):
        if inline and not result.rendered_inline:
            print(result.rendered_output.splitlines()[0])
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(result.rendered_output, end="")
        return
    # 兼容在本地调用 emit_result 输出自行加工的结果。
    root = Path.cwd() / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    previous_root = api._SESSION_CACHE.get("_root")
    api._SESSION_CACHE["_root"] = str(root)
    try:
        serialized = json.dumps(result, ensure_ascii=False, indent=2)
        path = api.resolve_data_path(slug, time.time())
        Path(path).write_text(serialized, encoding="utf-8")
        print(f"Saved full response: {path} ({len(serialized)} bytes)")
        if inline or len(serialized.encode("utf-8")) <= api.SMALL_THRESHOLD:
            print(serialized)
        else:
            api.summarize(result)
    finally:
        if previous_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = previous_root
