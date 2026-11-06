"""通过公共调用器执行请求，支持公开 GET、截止时间和诊断。

同步业务封装使用短作用域适配；网络连接始终由 call_api.call_api 发起。
不缓存，不重试，不向模型配置服务发送生成密钥或会话头。
"""
import io
import json
import os
from contextlib import redirect_stdout, redirect_stderr
from http.client import HTTPException
from unittest.mock import patch
from urllib.error import HTTPError, URLError

import call_api


def _error(code, message, raw=b"", status=None, headers=None):
    headers = headers or {}
    result = {"error": message, "errorCode": code, "responseBytes": len(raw)}
    if status is not None:
        result["httpStatus"] = status
    for field, value in (("contentType", headers.get("Content-Type")),
                         ("requestId", headers.get("X-Request-Id") or headers.get("X-Kong-Request-Id"))):
        if value:
            result[field] = value
    if raw:
        result["details"] = raw.decode("utf-8", errors="replace")
    return result


def _normal_response(raw, status, headers, aigc_codes=False):
    if not raw.strip():
        return _error("EMPTY_RESPONSE", f"上游返回空响应（HTTP {status}）", raw, status, headers)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return _error("INVALID_ENCODING", "上游响应不是 UTF-8", raw, status, headers)
    try:
        payload = json.loads(text)
    except ValueError:
        return _error("INVALID_JSON_RESPONSE", "上游响应不是 JSON", raw, status, headers)
    if not isinstance(payload, dict):
        return _error("INVALID_RESPONSE", "上游 JSON 响应必须为对象", raw, status, headers)
    # 只用 errcode 判断公共业务状态，不能把 0/false 当作空值。
    code = payload.get("errcode")
    empty = code is None or isinstance(code, str) and not code.strip()
    valid = empty
    if not empty:
        value = code.strip() if isinstance(code, str) else code
        if isinstance(value, str):
            valid = len(value) == 3 and value.isascii() and value.isdigit() and 200 <= int(value) < 300
        else:
            valid = type(value) in (int, float) and 200 <= value < 300 and value % 1 == 0
    # 生成接口兼容 code，并识别 errorCode。
    # 这是业务层检查；公共 errcode 规则仍然独立生效。
    business_code, business_failed = None, False
    if aigc_codes and "errcode" not in payload:
        if payload.get("code") is not None:
            business_code = payload["code"]
            business_failed = str(business_code) not in ("0", "200")
        elif payload.get("errorCode") is not None:
            business_code = payload["errorCode"]
            business_failed = str(business_code) != "200"
    if payload.get("error") or not valid or business_failed or not 200 <= status < 300:
        message = payload.get("error") or payload.get("errmsg") or payload.get("msg") or payload.get("message") or f"HTTP {status}: 上游请求失败"
        payload["error"] = message
        payload.setdefault("errorCode", str(code) if not valid else str(business_code) if business_failed else "HTTP_ERROR")
        metadata = _error(payload["errorCode"], message, raw, status, headers)
        for field in ("httpStatus", "contentType", "requestId", "responseBytes"):
            if field in metadata:
                payload.setdefault(field, metadata[field])
    return payload


class _Response:
    """公共传输读取响应时保留原始诊断，连接仍由公共传输管理。"""
    def __init__(self, response, aigc_codes=False):
        self.response = response
        self.status = response.status
        self.aigc_codes = aigc_codes

    def __enter__(self):
        self.response.__enter__()
        return self

    def __exit__(self, *args):
        return self.response.__exit__(*args)

    def read(self):
        try:
            raw = self.response.read()
            result = _normal_response(raw, self.status, self.response.headers, self.aigc_codes)
        except (OSError, HTTPException) as error:
            result = _error("HTTP_READ_ERROR", "无法读取上游响应；提交结果可能未知", getattr(error, "partial", b""), self.status, self.response.headers)
        return json.dumps(result, ensure_ascii=False).encode("utf-8")


def request_json(path, params, *, slug, timeout=150, public_get=False,
                 absolute_url=None, persist=True, aigc_codes=False):
    """调用 run 并返回响应对象；始终传 --no-cache，不缓存响应。"""
    if not public_get:
        call_api.get_api_key()
    original_request = call_api.Request
    original_open = call_api.urlopen
    original_call = call_api.call_api
    observed = {}

    def make_request(url, data=None, headers=None, method=None):
        if public_get:
            return original_request(url, headers={"Referer": "https://wiki.linkfox.com/", "User-Agent": "LinkFox-Skill/2.0"}, method="GET")
        return original_request(url, data=data, headers=headers, method=method)

    def open_response(request, timeout=150):
        # 仅为公共传输调整本次超时、读取和错误格式，没有另一条发送路径。
        try:
            return _Response(original_open(request, timeout=min(timeout, request_timeout)), aigc_codes)
        except HTTPError as error:
            try:
                raw = error.read() if error.fp else b""
                result = _normal_response(raw, error.code, error.headers or {}, aigc_codes)
            except (OSError, HTTPException) as read_error:
                result = _error("HTTP_READ_ERROR", "无法读取上游错误响应", getattr(read_error, "partial", b""), error.code, error.headers)
            raise HTTPError(error.url, error.code, error.reason, error.headers,
                            io.BytesIO(json.dumps(result, ensure_ascii=False).encode("utf-8"))) from error
        except URLError as error:
            code = "REQUEST_TIMEOUT" if isinstance(error.reason, TimeoutError) else "CONNECTION_ERROR"
            observed["failure"] = _error(code, "请求超时；提交结果可能未知" if code == "REQUEST_TIMEOUT" else f"连接失败：{error.reason}")
            raise
        except TimeoutError:
            observed["failure"] = _error("REQUEST_TIMEOUT", "请求超时；提交结果可能未知")
            raise
        except (OSError, HTTPException) as error:
            observed["failure"] = _error("HTTP_READ_ERROR", "无法读取上游响应；提交结果可能未知", getattr(error, "partial", b""))
            raise

    def record_call(api_path, values):
        try:
            status, payload = original_call(api_path, values)
        except (OSError, HTTPException):
            status, payload = None, observed.get("failure", _error("CONNECTION_ERROR", "上游连接失败"))
        payload = observed.get("failure", payload)
        observed.update(status=status, payload=payload)
        return status, payload

    request_timeout = timeout
    # 捕获公共 run 的原始输出，防止临时媒体 URL、诊断正文或 STS 凭证泄露。
    with patch.object(call_api, "Request", make_request), \
         patch.object(call_api, "urlopen", open_response), \
         patch.object(call_api, "call_api", record_call), \
         patch.object(call_api, "_cache_path", lambda *_: os.devnull), \
         redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
        from contextlib import ExitStack
        with ExitStack() as stack:
            if absolute_url is not None:
                stack.enter_context(patch.object(call_api, "get_api_url", lambda _: absolute_url))
            if public_get:
                stack.enter_context(patch.object(call_api, "get_api_key", lambda: ""))
            if not persist:
                # 上传凭证不落盘；目录由 save_catalog 负责存档并容忍存档失败。
                stack.enter_context(patch.object(call_api, "_resolve_output_path", lambda *_: os.devnull))
            try:
                call_api.run(path, slug, [json.dumps(params, ensure_ascii=False), "--inline", "--no-cache"])
            except OSError:
                if "payload" not in observed:
                    raise
    return observed["payload"]
