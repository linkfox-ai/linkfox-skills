"""通过公共 run 调用接口，并隔离其展示输出，保留生文 CLI 契约。"""

import contextlib
import io
import json
import tempfile
import time
from pathlib import Path

import call_api as api


def session_id(ts):
    """接口原始响应、业务输出和上传记录共用同一会话标识。"""
    return api._session_id(ts)


def code_ok(value):
    if value is None:
        return True
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return True
        if len(value) != 3 or not value.isascii() or not value.isdigit():
            return False
        value = int(value)
    return type(value) in (int, float) and 200 <= value < 300 and value % 1 == 0


def response_failed(result):
    if not isinstance(result, dict) or "error" in result:
        return True
    http_status = result.get("transportHttpStatus", 200)
    if type(http_status) is not int or not 200 <= http_status < 300:
        return True
    return any(not code_ok(result.get(k)) for k in ("errcode", "errorCode", "code"))


def retryable(result):
    """仅重试暂时的传输故障；本地错误及认证、用量错误立即停止。"""
    if result.get("localError"):
        return False
    if any(str(result.get(k)).strip() in ("401", "402", "403")
           for k in ("errcode", "errorCode", "code")):
        return False
    message = " ".join(str(result.get(k, "")) for k in ("errmsg", "message", "error")).lower()
    if any(marker in message for marker in (
        "authorized error", "unauthorized", "insufficient", "quota", "鉴权", "未授权",
        "余额不足", "算力不足", "计费不足", "套餐到期", "充值",
    )):
        return False
    status = result.get("transportHttpStatus", 200)
    return status in (408, 429, 500, 502, 503, 504) or (status is None and "error" in result)


def run_json(path, params, slug, *, sensitive=False, timeout=150):
    """无缓存调用；捕获真实 HTTP 状态；敏感凭证仅在内存中交给上传器。"""
    transport = api.call_api
    old_urlopen = api.urlopen
    old_output = api._resolve_output_path
    old_root = api._SESSION_CACHE.get("_root")
    captured = {}
    # 与金例一致：必须在 cwd 保存，不能静默回退到临时目录。
    root = Path.cwd() / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    api._SESSION_CACHE["_root"] = str(root)

    def capture(api_path, request_params):
        try:
            status, body = transport(api_path, request_params)
        except OSError as exc:
            status, body = None, {"error": f"连接失败：{exc}"}
        captured.update(status=status, body=body)
        if sensitive:
            return status, {"transportHttpStatus": status, "凭证响应": "已隐藏，仅在内存中使用"}
        return status, body if isinstance(body, dict) else {"error": "接口响应不是对象", "response": body}

    def output_path(output_slug, _ts):
        output = api.resolve_data_path(output_slug, time.time())
        captured["savedPath"] = output
        return output

    api.call_api = capture
    api._resolve_output_path = output_path
    timeout_override = timeout
    api.urlopen = lambda request, timeout=150: old_urlopen(request, timeout=timeout_override)
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            api.run(path, slug, argv=[json.dumps(params, ensure_ascii=False), "--inline", "--no-cache"])
    finally:
        api.call_api = transport
        api.urlopen = old_urlopen
        api._resolve_output_path = old_output
        if old_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = old_root
    if not Path(captured["savedPath"]).is_file():
        raise OSError("接口响应保存失败")
    result = captured["body"]
    if not isinstance(result, dict):
        result = {"error": "接口响应不是对象", "transportHttpStatus": captured["status"]}
        if not sensitive:
            result["response"] = captured["body"]
        return result
    result = dict(result)
    if captured["status"] is None or not 200 <= captured["status"] < 300:
        result["transportHttpStatus"] = captured["status"]
    return result
