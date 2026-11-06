"""在公共调用器上保留 AIGC 的 GET、超时、诊断和静默媒体交付约定。

仅顺序调用；临时适配公共模块后始终恢复，不另建 HTTP transport 或响应缓存。
"""
import io
import json
import os
import sys
import threading
import time
from contextlib import redirect_stdout, redirect_stderr
from http.client import HTTPException
from urllib.error import HTTPError, URLError

import call_api

_LOCK = threading.RLock()


def _error(code, message, raw=b"", status=None, headers=None):
    result = {"error": message, "errorCode": code, "responseBytes": len(raw)}
    if status is not None:
        result["httpStatus"] = status
    headers = headers or {}
    for field, value in (("contentType", headers.get("Content-Type")),
                         ("requestId", headers.get("X-Request-Id") or headers.get("X-Kong-Request-Id"))):
        if value:
            result[field] = value
    if raw:
        result["details"] = raw.decode("utf-8", errors="replace")
    return result


def _decode_response(raw, status, headers):
    if not raw.strip():
        return _error("EMPTY_RESPONSE", "上游返回空响应", raw, status, headers)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return _error("INVALID_ENCODING", "上游响应不是 UTF-8", raw, status, headers)
    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        return _error("INVALID_JSON_RESPONSE", "上游响应不是 JSON", raw, status, headers)
    if not isinstance(result, dict):
        return _error("INVALID_RESPONSE", "上游 JSON 响应必须是对象", raw, status, headers)
    # 按公共调用器完整判断 errcode，HTTP 允许所有 2xx；0/false 不是空值。
    business_ok = call_api._is_cacheable(200, result)
    if result.get("error") or not business_ok or not (status is not None and 200 <= status < 300):
        message = result.get("error") or result.get("errmsg") or result.get("msg") or result.get("message") or "上游请求失败"
        result["error"] = message
        result.setdefault("errorCode", str(result.get("errcode")) if not business_ok else "HTTP_ERROR")
        metadata = _error(result["errorCode"], message, raw, status, headers)
        for key in ("httpStatus", "contentType", "requestId", "responseBytes"):
            if key in metadata:
                result.setdefault(key, metadata[key])
    return result


def request(api_path, slug, params, *, timeout=150, public_url=None, raise_transport_errors=False):
    """通过 call_api.run 调用一次；公共目录使用独立地址且不发送网关身份头。"""
    with _LOCK:
        original = {name: getattr(call_api, name) for name in
                    ("call_api", "Request", "urlopen", "get_api_url", "get_api_key", "_cache_path")}
        state = {"raw": b"", "status": None, "headers": {}, "result": None}

        def make_request(url, data=None, headers=None, method=None):
            if public_url is not None:
                return original["Request"](url, method="GET", headers={
                    "Referer": "https://wiki.linkfox.com/", "User-Agent": "LinkFox-Skill/2.0"})
            return original["Request"](url, data=data, headers=headers, method=method)

        class Response:
            def __init__(self, response):
                self.response = response
                self.status = response.status
                state.update(status=response.status, headers=response.headers)

            def __enter__(self):
                self.response.__enter__()
                return self

            def __exit__(self, *args):
                return self.response.__exit__(*args)

            def read(self):
                state["raw"] = self.response.read()
                return state["raw"]

        def open_response(req, **kwargs):
            try:
                return Response(original["urlopen"](req, timeout=timeout))
            except HTTPError as error:
                state.update(status=error.code, headers=error.headers or {})
                state["transport_exception"] = error
                read = error.read

                def read_error(*args, **kw):
                    state["raw"] = read(*args, **kw)
                    return state["raw"]

                error.read = read_error
                raise
            except URLError as error:
                state["connection_error"] = error
                raise

        def invoke(path, body):
            try:
                status, result = original["call_api"](path, body)
                if "connection_error" in state:
                    raise state["connection_error"]
                if state["status"] is not None:
                    result = _decode_response(state["raw"], state["status"], state["headers"])
                elif status is not None:
                    result = _decode_response(json.dumps(result).encode("utf-8"), status, {})
            except (UnicodeError, ValueError) as error:
                state.setdefault("transport_exception", error)
                status = state["status"]
                result = _decode_response(state["raw"], status, state["headers"])
            except URLError as error:
                state.setdefault("transport_exception", error)
                status = None
                code = "REQUEST_TIMEOUT" if isinstance(error.reason, TimeoutError) else "CONNECTION_ERROR"
                result = _error(code, "请求超时，提交结果可能未知" if code == "REQUEST_TIMEOUT" else f"连接失败：{error.reason}")
            except TimeoutError as error:
                state.setdefault("transport_exception", error)
                status = state["status"]
                result = _error("REQUEST_TIMEOUT", "请求超时，提交结果可能未知", status=status, headers=state["headers"])
            except (OSError, HTTPException) as error:
                state.setdefault("transport_exception", error)
                status = state["status"]
                result = _error("HTTP_READ_ERROR", "无法读取上游响应，提交结果可能未知",
                                getattr(error, "partial", b""), status, state["headers"])
            state["result"] = result
            return status, result

        try:
            call_api.call_api = invoke
            call_api.Request = make_request
            call_api.urlopen = open_response
            # run 在判断 --no-cache 前会创建缓存目录。业务无响应缓存，跳过这项
            # 无用的磁盘准备；目录存档失败也不能阻止公共配置查询。
            call_api._cache_path = lambda slug, params: ""
            if public_url is not None:
                call_api.get_api_url = lambda path: public_url
                call_api.get_api_key = lambda: ""
            elif not (os.getenv("LINKFOX_AGENT_API_KEY") or os.getenv("LINKFOXAGENT_API_KEY")):
                return _error("MISSING_API_KEY", "API Key 未配置")
            # 业务无响应缓存；即使同 taskId 连续查询也必须取得当前状态。
            # 每次调用使用独立文件名，避免同秒多个请求覆盖原始响应。
            try:
                with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    call_api.run(api_path, slug + "-" + str(time.time_ns()),
                                 [json.dumps(params, ensure_ascii=False), "--no-cache"])
            except OSError as error:
                if state["result"] is None:
                    return _error("LOCAL_STORAGE_ERROR", f"本地数据目录不可写：{error}")
                # 已得到响应时保存异常不触发第二次请求，也不把有效空目录变成兜底。
                print(f"无法保存接口诊断：{error}", file=sys.stderr)
            # 目录助手用实际异常类型生成 fallbackReason；生成/上传返回结构化诊断。
            if raise_transport_errors and "transport_exception" in state:
                raise state["transport_exception"]
            return state["result"]
        finally:
            for name, value in original.items():
                setattr(call_api, name, value)
