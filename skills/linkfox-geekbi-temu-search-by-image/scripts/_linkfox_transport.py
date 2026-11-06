"""通过公共 run 调用网关；业务层负责缓存、落盘和输出。"""

import json
import os

import call_api as api


class _ResponseCaptured(Exception):
    """在公共调用器进入落盘阶段前，向业务封装返回完整响应。"""


def request(api_path, slug, params):
    """返回 (HTTP 状态码, 响应体)，不重复缓存、保存或打印响应。"""
    transport = api.call_api
    cache_path = api._cache_path
    output_path = api._resolve_output_path
    opener = api.urlopen
    previous_session = os.environ.get("SESSION_ID")
    captured = None
    response_status = None
    http_error = None

    def open_response(*args, **kwargs):
        nonlocal response_status, http_error
        try:
            response = opener(*args, **kwargs)
        except api.HTTPError as exc:
            response_status = exc.code
            http_error = exc
            raise
        response_status = response.status
        return response

    def capture(path, payload):
        nonlocal captured
        try:
            captured = transport(path, payload)
        except json.JSONDecodeError as exc:
            captured = (response_status, {"error": "Invalid JSON response", "details": exc.doc[:500]})
        except UnicodeDecodeError as exc:
            text = exc.object.decode("utf-8", errors="replace")
            if http_error is not None:
                # HTTP 错误保留状态、原因和可解析的业务体，不混同连接失败。
                try:
                    result = json.loads(text)
                except json.JSONDecodeError:
                    result = {"error": f"HTTP {response_status}: {http_error.reason}", "details": text[:500]}
            else:
                result = {"error": "Invalid UTF-8 response", "details": text[:500]}
            captured = (response_status, result)
        except TimeoutError:
            captured = (response_status, {"error": "Connection timed out"})
        status, result = captured
        if isinstance(result, dict) and isinstance(result.get("details"), str):
            result["details"] = result["details"][:500]
        return status, result

    def finish(_slug, _ts):
        raise _ResponseCaptured

    # --no-cache 禁用读写；覆盖路径解析，避免 run 额外创建空缓存目录。
    # 业务脚本负责完整的缓存与输出流程，公共调用器只承担网关 HTTP。
    api.call_api = capture
    api.urlopen = open_response
    api._cache_path = lambda *_: os.devnull
    api._resolve_output_path = finish
    os.environ["SESSION_ID"] = (previous_session or "").strip()
    try:
        try:
            api.run(api_path, slug, argv=[json.dumps(params, ensure_ascii=False), "--no-cache"])
        except _ResponseCaptured:
            return captured
        raise RuntimeError("公共调用器未返回响应")
    finally:
        api.call_api = transport
        api.urlopen = opener
        api._cache_path = cache_path
        api._resolve_output_path = output_path
        if previous_session is None:
            os.environ.pop("SESSION_ID", None)
        else:
            os.environ["SESSION_ID"] = previous_session


def is_success(status, payload):
    """与 references 中的公共响应码规则一致。"""
    if status is None or not 200 <= status < 300 or not isinstance(payload, dict):
        return False
    # 公共函数仅在 HTTP 200 时检查缓存；此处已独立核对外层 2xx。
    return api._is_cacheable(200, payload)
