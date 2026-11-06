"""订单参数映射与公共调用器适配；使用 sellerId 和 region，不启用响应缓存。"""
from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

import call_api as api

SLUG = "linkfox-amazon-store-orders"
API_BASE_URL = (os.environ.get("LINKFOX_TOOL_GATEWAY") or os.environ.get("STORE_API_BASE_URL")
                or os.environ.get("SPAPI_BASE_URL") or "https://tool-gateway.linkfox.com").rstrip("/")
REQUIRED_SKILL = "linkfox-amazon-store-auth"
DEPENDENCY_EXIT_CODE = 42
get_api_key = api.get_api_key


def load_cli_params() -> dict:
    """解析业务 CLI 的 JSON 对象，错误输入在请求前退出。"""
    try:
        params = json.loads(sys.argv[1])
    except json.JSONDecodeError as exc:
        print(f"JSON 参数无效：{exc}", file=sys.stderr)
        raise SystemExit(1)
    if not isinstance(params, dict):
        print("JSON 参数必须为对象。", file=sys.stderr)
        raise SystemExit(1)
    return params


def require_fields(params: dict, fields) -> None:
    """校验必填项，拒绝缺失、null 和纯空白标识。"""
    for field in fields:
        if field not in params or params[field] is None or not str(params[field]).strip():
            print(f"缺少或为空的必填字段：{field}", file=sys.stderr)
            raise SystemExit(1)


def ensure_auth_skill_available(caller: str = "orders script") -> None:
    checker = Path(__file__).resolve().parent / "check_auth_dependency.py"
    if not checker.exists():
        payload = {"missingSkill": REQUIRED_SKILL, "reason": f"check_auth_dependency.py not found next to {caller}"}
        print(f"DEPENDENCY_MISSING: {json.dumps(payload, ensure_ascii=False)}", file=sys.stderr)
        raise SystemExit(DEPENDENCY_EXIT_CODE)
    try:
        result = subprocess.run([sys.executable, str(checker)], capture_output=True, text=True, timeout=10)
    except Exception as exc:
        payload = {"missingSkill": REQUIRED_SKILL, "reason": str(exc)}
        print(f"DEPENDENCY_MISSING: {json.dumps(payload, ensure_ascii=False)}", file=sys.stderr)
        raise SystemExit(DEPENDENCY_EXIT_CODE)
    if result.stderr:
        sys.stderr.write(result.stderr)
        if not result.stderr.endswith("\n"):
            sys.stderr.write("\n")
    if result.returncode != 0:
        raise SystemExit(DEPENDENCY_EXIT_CODE)


def _invoke(api_path, params, operation, transform, *, quiet=False):
    """公共 run 执行唯一一次传输；加工后的响应统一保存和展示。"""
    root = Path.cwd() / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    # 请求前验证工作目录可写，禁止公共调用器回退到家目录或临时目录。
    with tempfile.TemporaryFile(dir=root):
        pass
    transport = api.call_api
    previous_output = api._resolve_output_path
    previous_root = api._SESSION_CACHE.get("_root")
    previous_gateway = os.environ.get("LINKFOX_TOOL_GATEWAY")
    captured = {}

    def receive(path, request):
        status, payload = transport(path, request)
        captured["payload"] = payload
        return status, transform(status, payload)

    api.call_api = receive
    api._SESSION_CACHE["_root"] = str(root)
    api._resolve_output_path = lambda slug, _ts: api.resolve_data_path(slug, time.time())
    if not previous_gateway:
        os.environ["LINKFOX_TOOL_GATEWAY"] = (os.environ.get("STORE_API_BASE_URL")
                                                or os.environ.get("SPAPI_BASE_URL") or API_BASE_URL)
    try:
        argv = [json.dumps(params, ensure_ascii=False), "--no-cache"]
        if "--inline" in sys.argv[1:]:
            argv.append("--inline")
        if quiet:
            with redirect_stdout(io.StringIO()):
                api.run(api_path, f"{SLUG}-{operation}", argv=argv)
        else:
            api.run(api_path, f"{SLUG}-{operation}", argv=argv)
    finally:
        api.call_api = transport
        api._resolve_output_path = previous_output
        if previous_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = previous_root
        if previous_gateway is None:
            os.environ.pop("LINKFOX_TOOL_GATEWAY", None)
        else:
            os.environ["LINKFOX_TOOL_GATEWAY"] = previous_gateway
    return captured["payload"]


def merge_json_body(out: dict, proxy: dict, key: str) -> None:
    """上游为 200 且网关状态正常时解析 body，保留解析失败的原文。"""
    if not isinstance(proxy, dict) or not api._is_cacheable(200, proxy):
        return
    status = proxy.get("httpStatus")
    if isinstance(status, bool) or str(status).strip() != "200":
        return
    raw = proxy.get("body")
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        out[key] = None
        return
    try:
        out[key] = json.loads(raw) if isinstance(raw, str) else raw
    except (TypeError, json.JSONDecodeError):
        out[key] = None
        out[key + "Raw"] = raw


def run_proxy(operation, region, path, method, seller_id, *, query_string=None,
              result_field=None, body_obj=None):
    params: dict[str, Any] = {"region": region, "path": path, "method": method, "sellerId": seller_id}
    if query_string:
        params["queryString"] = query_string
    if body_obj is not None:
        params["body"] = json.dumps(body_obj, ensure_ascii=False)
        params["contentType"] = "application/json"

    def result(status, proxy):
        out = {"developerProxy": proxy, "resolvedPath": path, "transportHttpStatus": status}
        if query_string is not None or operation in ("searchOrders", "getOrder", "getOrderItems", "getOrderItemsBuyerInfo"):
            out["queryString"] = query_string
        if body_obj is not None:
            out["requestBody"] = body_obj
        if result_field and type(status) is int and 200 <= status < 300:
            merge_json_body(out, proxy, result_field)
        return out

    return _invoke("/spApi/developerProxy", params, operation, result)


