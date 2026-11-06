"""Shopee 授权脚本的参数兼容与调用编排；HTTP、落盘和摘要统一交给公共调用器。"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from pathlib import Path

import call_api as api

SLUG = "linkfox-shopee-store-auth"


def read_params(usage, *, optional=False):
    """支持位置 JSON、无参数店铺列表、--inline 和无需网络请求的帮助。"""
    argv = sys.argv[1:]
    if "--help" in argv or "-h" in argv:
        print(usage)
        raise SystemExit(0)
    positional = [arg for arg in argv if arg not in ("--inline", "--no-cache")]
    if not positional and optional:
        return {}
    if len(positional) != 1:
        print(usage, file=sys.stderr)
        raise SystemExit(1)
    try:
        params = json.loads(positional[0])
    except json.JSONDecodeError as exc:
        print(f"JSON 参数格式错误：{exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    if not isinstance(params, dict):
        print("JSON 参数必须是对象。", file=sys.stderr)
        raise SystemExit(1)
    return params


def normalize_app_type(params):
    raw = params.get("appType")
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        params["appType"] = "erp"
    else:
        app_type = str(raw).strip().lower()
        if app_type not in ("erp", "ad"):
            print(f"appType 必须为 erp 或 ad，收到 {raw!r}。", file=sys.stderr)
            raise SystemExit(1)
        params["appType"] = app_type


def displayed_app_type(store):
    """历史缺省与空白应用类型属于 ERP，不能当作广告授权。"""
    raw = store.get("appType", store.get("app_type"))
    if raw is None or not str(raw).strip():
        return "erp"
    return str(raw).strip().lower()


def run_request(endpoint, operation, params, *, transform=None):
    """只调用一次 run；在公共落盘前完成业务脱敏，并禁用响应缓存。"""
    root = Path.cwd() / "linkfox"
    transport = api.call_api
    previous_output_path = api._resolve_output_path
    previous_root = api._SESSION_CACHE.get("_root")
    previous_workspace = os.environ.get("ACPX_WORKSPACES")
    previous_gateway = os.environ.get("LINKFOX_TOOL_GATEWAY")
    received = {}

    def process_response(api_path, request_params):
        http_status, raw = transport(api_path, request_params)
        result = transform(raw) if transform is not None else raw
        if not isinstance(result, dict):
            # 公共调用器按 JSON 对象输出；异常形态仍保存，避免打印成功提示。
            result = {"error": "接口响应不是 JSON 对象", "response": result}
            received["invalid_shape"] = True
        if type(http_status) is not int or not 200 <= http_status < 300:
            # 公共调用器只保存响应体；业务层补存传输状态，避免 JSON 错误体丢失 HTTP 证据。
            result = dict(result)
            result["_http_status"] = http_status
        received.update(http_status=http_status, result=result)
        return http_status, result

    os.environ["ACPX_WORKSPACES"] = str(Path.cwd())
    if not previous_gateway:
        os.environ["LINKFOX_TOOL_GATEWAY"] = (
            os.environ.get("SHOPEE_API_BASE_URL") or api.get_api_base()
        )
    api._SESSION_CACHE["_root"] = str(root)
    api.call_api = process_response
    try:
        # 检查真正的会话数据目录；根目录可写不代表已有会话目录也可写。
        # 在请求前确定微秒文件名，避免公共 run 的整秒时间导致响应覆盖。
        output_path = api.resolve_data_path(f"{SLUG}-{operation}", time.time())
        with tempfile.TemporaryFile(dir=Path(output_path).parent):
            pass
        api._resolve_output_path = lambda _slug, _ts: output_path
        argv = [json.dumps(params, ensure_ascii=False), "--no-cache"]
        if "--inline" in sys.argv[1:]:
            argv.append("--inline")
        api.run(endpoint, f"{SLUG}-{operation}", argv=argv)
    finally:
        api.call_api = transport
        api._resolve_output_path = previous_output_path
        if previous_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = previous_root
        for name, old in (("ACPX_WORKSPACES", previous_workspace),
                          ("LINKFOX_TOOL_GATEWAY", previous_gateway)):
            if old is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = old

    status = received.get("http_status")
    result = received["result"]
    code = result.get("errcode")
    legacy_success = (type(code) is int and code == 0
                      or isinstance(code, str) and code.strip() == "0")
    # 0 是授权接口的兼容成功码；公共缓存规则保持不变。
    code_ok = api._is_cacheable(200, result)
    if legacy_success:
        code_ok = not result.get("error") and result.get("success") is not False
    normal = type(status) is int and 200 <= status < 300 and not received.get("invalid_shape") and code_ok
    if not normal:
        print(f"请求未正常响应（HTTP {status}）；详情已保存，请按接口说明处理，不自动重试。",
              file=sys.stderr)
        raise SystemExit(1)
    return result
