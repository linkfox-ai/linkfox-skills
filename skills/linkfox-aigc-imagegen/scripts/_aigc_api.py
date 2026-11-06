"""保留 AIGC 协议差异；所有 LinkFox HTTP 仍由公共 call_api.run 发起。"""

import contextlib
import io
import json
import os
import threading
from http.client import HTTPException
from urllib.error import HTTPError, URLError

import call_api

_LOCK = threading.RLock()


def response_error(code, message, raw=b"", status=None, headers=None):
    headers = headers or {}
    result = {"error": message, "errorCode": code, "responseBytes": len(raw)}
    if status is not None:
        result["httpStatus"] = status
    for key, value in (("contentType", headers.get("Content-Type")),
                       ("requestId", headers.get("X-Request-Id") or headers.get("X-Kong-Request-Id"))):
        if value:
            result[key] = value
    if raw:
        result["details"] = raw.decode("utf-8", errors="replace")
    return result


def decode_response(raw, status, headers):
    if not raw.strip():
        return response_error("EMPTY_RESPONSE", f"Upstream returned an empty response (HTTP {status})", raw, status, headers)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return response_error("INVALID_ENCODING", f"Upstream response is not UTF-8 (HTTP {status})", raw, status, headers)
    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        return response_error("INVALID_JSON_RESPONSE", f"Upstream response is not JSON (HTTP {status})", raw, status, headers)
    if not isinstance(result, dict):
        return response_error("INVALID_RESPONSE", "Upstream JSON response must be an object", raw, status, headers)
    # 与金例的 errcode 基础规则一致，0/false 不视为空。
    code = result.get("errcode")
    if isinstance(code, str):
        code = code.strip()
        valid_code = not code or (len(code) == 3 and code.isascii() and code.isdigit() and 200 <= int(code) < 300)
    else:
        valid_code = code is None or (type(code) in (int, float) and 200 <= code < 300 and code % 1 == 0)
    # 原业务还兼容仅有 code 的响应；独立于公共 errcode 基础规则。
    legacy_code = result.get("code") if "errcode" not in result else None
    legacy_failed = legacy_code is not None and str(legacy_code) not in ("0", "200")
    if result.get("error") or not valid_code or legacy_failed or status is None or not 200 <= status < 300:
        message = result.get("error") or result.get("errmsg") or result.get("msg") or result.get("message") or f"HTTP {status}: upstream request failed"
        result["error"] = message
        result.setdefault("errorCode", str(code) if not valid_code else str(legacy_code) if legacy_failed else "HTTP_ERROR")
        metadata = response_error(result["errorCode"], message, raw, status, headers)
        for key in ("httpStatus", "contentType", "requestId", "responseBytes"):
            if key in metadata:
                result.setdefault(key, metadata[key])
    return result


def request_json(api_path, params, slug, *, timeout=150, public_url=None, private=False):
    """通过未修改的 run 调用；适配公开 GET、请求时限及凭证不落盘。

    公共脚本没有 GET/timeout/返回值参数，因此在锁内临时适配其 Request、
    urlopen 和结果路径，并观察原 transport 的响应；不另建 HTTP transport。
    """
    with _LOCK, contextlib.ExitStack() as stack:
        native_transport = call_api.call_api
        native_request = call_api.Request
        native_open = call_api.urlopen
        observed = {"raw": b"", "status": None, "headers": {}}
        captured = {}

        def replace(name, value):
            previous = getattr(call_api, name)
            setattr(call_api, name, value)
            stack.callback(setattr, call_api, name, previous)

        class Response:
            def __init__(self, response):
                self.response = response

            def __enter__(self):
                self.response.__enter__()
                observed.update(status=self.response.status, headers=self.response.headers)
                return self

            def __exit__(self, *args):
                return self.response.__exit__(*args)

            @property
            def status(self):
                return self.response.status

            def read(self):
                observed["raw"] = self.response.read()
                return observed["raw"]

        def open_response(request, **kwargs):
            try:
                return Response(native_open(request, timeout=timeout))
            except HTTPError as error:
                observed.update(status=error.code, headers=error.headers or {})
                observed["raw"] = error.read() if error.fp else b""
                error.fp = io.BytesIO(observed["raw"])
                raise
            except URLError as error:
                observed["exception"] = error
                raise

        def transport(path, body):
            try:
                status, payload = native_transport(path, body)
                if "exception" in observed:
                    raise observed["exception"]
                payload = decode_response(observed["raw"], observed["status"], observed["headers"])
            except (UnicodeError, ValueError):
                status = observed["status"]
                payload = decode_response(observed["raw"], status, observed["headers"])
            except URLError as error:
                status = observed["status"]
                timed_out = isinstance(error.reason, TimeoutError)
                payload = response_error("REQUEST_TIMEOUT" if timed_out else "CONNECTION_ERROR",
                                         "Request timed out; submission outcome may be unknown" if timed_out else f"Connection failed: {error.reason}")
            except TimeoutError:
                status = observed["status"]
                payload = response_error("REQUEST_TIMEOUT", "Request timed out; submission outcome may be unknown", status=status, headers=observed["headers"])
            except (OSError, HTTPException) as error:
                status = observed["status"]
                payload = response_error("HTTP_READ_ERROR", "Could not read upstream response; submission outcome may be unknown", getattr(error, "partial", b""), status, observed["headers"])
            captured.update(status=status, payload=payload)
            return status, payload

        replace("urlopen", open_response)
        replace("call_api", transport)
        # run 即使 --no-cache 也会先建缓存目录；原 AIGC 不依赖此目录。
        replace("_cache_path", lambda slug, body: os.devnull)
        if public_url is not None:
            replace("get_api_url", lambda path: public_url)
            replace("get_api_key", lambda: "")

            def public_request(url, **kwargs):
                return native_request(url, method="GET", headers={"Referer": "https://wiki.linkfox.com/", "User-Agent": "LinkFox-Skill/2.0"})

            replace("Request", public_request)
        # 原业务封装负责最终响应/失败诊断与目录存档。中间轮询不新增落盘：
        # 避免公共调用器另建自动会话、整秒文件相互覆盖，或存档失败中断原任务。
        # private 凭证同样只保留在内存中，不写入任何响应文件。
        replace("_resolve_output_path", lambda slug, ts: os.devnull)
        with contextlib.redirect_stdout(io.StringIO()):
            call_api.run(api_path, slug, [json.dumps(params, ensure_ascii=False), "--inline", "--no-cache"])
        return captured["status"], captured["payload"]
