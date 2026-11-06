"""通过公共 run 调用网关；缓存与业务输出仍由入库执行器管理。"""

from __future__ import annotations

import contextlib
import io
import json
import os
import time

import call_api as api

API_PATH = "/spApi/developerProxy"
SLUG = "linkfox-amazon-store-fulfillment-inbound"


class ProxyResponse(dict):
    """保留网关原始字段，同时携带外层 HTTP 状态。"""

    def __init__(self, payload, http_status):
        super().__init__(payload)
        self.transport_http_status = http_status


def get_api_base() -> str:
    return (
        os.environ.get("LINKFOX_TOOL_GATEWAY")
        or os.environ.get("STORE_API_BASE_URL")
        or os.environ.get("SPAPI_BASE_URL")
        or "https://tool-gateway.linkfox.com"
    ).rstrip("/")


def call_api(params):
    # 延迟导入，使用入库执行器的严格 cwd、会话清理及完整业务输出规则。
    from _spapi_fulfillment_inbound_common import _lf_root, _lf_session_id

    root = _lf_root()  # 请求前检查可写性，不允许公共调用器回退到其他目录。
    transport = api.call_api
    previous_path = api._resolve_output_path
    previous_session_id = api._session_id
    previous_root = api._SESSION_CACHE.get("_root")
    previous_env = {"LINKFOX_TOOL_GATEWAY": os.environ.get("LINKFOX_TOOL_GATEWAY")}
    response = None

    def capture(api_path, request_params):
        nonlocal response
        http_status, payload = transport(api_path, request_params)
        if not isinstance(payload, dict):
            payload = {"error": "网关响应不是 JSON 对象", "rawResponse": payload}
        response = ProxyResponse(payload, http_status)
        return http_status, payload

    os.environ["LINKFOX_TOOL_GATEWAY"] = get_api_base()
    # 仅落盘目录使用清理后的会话名，请求头继续透传原始 SESSION_ID。
    api._session_id = _lf_session_id
    api._SESSION_CACHE["_root"] = root
    api.call_api = capture
    # 公共脚本默认秒级命名；保留每次原始响应，避免同秒覆盖。
    api._resolve_output_path = lambda slug, _ts: api.resolve_data_path(slug, time.time())
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            api.run(API_PATH, SLUG + "-raw", argv=[json.dumps(params, ensure_ascii=False), "--no-cache"])
        if response is None:
            raise RuntimeError("公共调用器未返回网关响应")
        return response
    finally:
        api.call_api = transport
        api._resolve_output_path = previous_path
        api._session_id = previous_session_id
        if previous_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = previous_root
        for key, value in previous_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


if __name__ == "__main__":
    raise SystemExit("内部模块，请运行固定操作脚本")
