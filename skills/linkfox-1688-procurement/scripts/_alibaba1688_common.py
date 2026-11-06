#!/usr/bin/env python3
"""1688 采购业务 CLI：授权前检、独立确认、脱敏与可选落盘。"""

import json
import os
import secrets
import sys
import tempfile
import time
import io
from contextlib import redirect_stdout
from unittest.mock import patch

import call_api as shared_api


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

SLUG = "linkfox-1688-procurement"
SMALL_THRESHOLD = 8000

ENDPOINTS = {
    "authorizeUrl": "/alibaba1688/authorizeUrl",
    "authorizedStores": "/alibaba1688/authorizedStores",
    "receiveAddressList": "/alibaba1688/receiveAddressList",
    "sku": "/alibaba1688/sku",
    "orderPreview": "/alibaba1688/orderPreview",
    "createOrder": "/alibaba1688/createOrder",
    "paymentUrl": "/alibaba1688/paymentUrl",
    "orderStatus": "/alibaba1688/orderStatus",
    "logistics": "/alibaba1688/logistics",
    "logisticsTrace": "/alibaba1688/logisticsTrace",
    "confirmReceive": "/alibaba1688/confirmReceive",
    "cancelOrder": "/alibaba1688/cancelOrder",
    "invoiceAmount": "/alibaba1688/invoiceAmount",
    "invoiceApply": "/alibaba1688/invoiceApply",
}

CONFIRM_FIELDS = {
    "createOrder": "confirmCreateOrder",
    "paymentUrl": "confirmGetPaymentUrl",
    "confirmReceive": "confirmReceive",
    "cancelOrder": "confirmCancel",
    "invoiceApply": "confirmApplyInvoice",
}

ORDER_FLOW_OPERATIONS = {"orderPreview", "createOrder"}
VALID_ORDER_FLOWS = {"general", "fenxiao", "boutiquefenxiao"}
VALID_USE_RED_ENVELOPE = {"y", "n"}

AUTH_PRECHECK_EXEMPT_OPERATIONS = {"authorizeUrl", "authorizedStores"}

SENSITIVE_KEYS = {
    "authorization",
    "api_key",
    "apikey",
    "appsecret",
    "access_token",
    "accesstoken",
    "refresh_token",
    "refreshtoken",
    "sessionkey",
    "jwt",
    "token",
    "secret",
    "callbackcode",
}

HIDDEN_OUTPUT_KEYS = {
    "tokenexpiresat",
}

_SESSION_CACHE = {}


def get_api_base():
    return (os.environ.get("LINKFOX_TOOL_GATEWAY") or "https://tool-gateway.linkfox.com").rstrip("/")


def get_api_key():
    """
    获取配置在环境变量的API Key。
    如果获取不到，按 SKILL.md 的 **## 解决认证和算力问题** 处理。
    """
    key = os.environ.get("LINKFOX_AGENT_API_KEY") or os.environ.get("LINKFOXAGENT_API_KEY")
    if not key:
        print(
            "API Key not configured. Set LINKFOX_AGENT_API_KEY or LINKFOXAGENT_API_KEY.",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


def _is_sensitive_key(key):
    normalized = str(key).replace("-", "").replace("_", "").lower()
    return normalized in SENSITIVE_KEYS


def _is_hidden_output_key(key):
    normalized = str(key).replace("-", "").replace("_", "").lower()
    return normalized in HIDDEN_OUTPUT_KEYS


def redact(value):
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            if _is_hidden_output_key(key):
                continue
            result[key] = "***REDACTED***" if _is_sensitive_key(key) else redact(item)
        return result
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value


def require_confirmation(operation, params):
    field = CONFIRM_FIELDS.get(operation)
    if not field:
        return
    if params.get(field) is True:
        return
    print(
        json.dumps(
            {
                "error": "confirmation_required",
                "operation": operation,
                "requiredField": field,
                "message": f"High-risk operation blocked locally. Provide JSON boolean {field}=true after separate explicit user confirmation.",
            },
            ensure_ascii=False,
            indent=2,
        ),
        file=sys.stderr,
    )
    sys.exit(2)


def normalize_params(operation, params):
    if operation == "createOrder":
        use_red_envelope = params.get("useRedEnvelope")
        if use_red_envelope is None or (isinstance(use_red_envelope, str) and not use_red_envelope.strip()):
            params["useRedEnvelope"] = "n"
        elif isinstance(use_red_envelope, str) and use_red_envelope.strip() in VALID_USE_RED_ENVELOPE:
            params["useRedEnvelope"] = use_red_envelope.strip()
        else:
            print(
                json.dumps(
                    {
                        "error": "invalid_parameter",
                        "operation": operation,
                        "field": "useRedEnvelope",
                        "message": "useRedEnvelope only supports y/n. Omit it to default to n.",
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                file=sys.stderr,
            )
            sys.exit(2)

    if operation not in ORDER_FLOW_OPERATIONS:
        return params

    flow = params.get("flow")
    if flow is None or (isinstance(flow, str) and not flow.strip()):
        params["flow"] = "general"
        return params

    if isinstance(flow, str):
        normalized_flow = flow.strip()
        if normalized_flow in VALID_ORDER_FLOWS:
            params["flow"] = normalized_flow
            return params

    print(
        json.dumps(
            {
                "error": "invalid_parameter",
                "operation": operation,
                "field": "flow",
                "message": "flow only supports general/fenxiao/boutiquefenxiao. Ordinary procurement should use general.",
            },
            ensure_ascii=False,
            indent=2,
        ),
        file=sys.stderr,
    )
    sys.exit(2)


class _ResponseJSON:
    """空响应解析为对象；其他 JSON 行为使用标准库。"""

    def loads(self, value, *args, **kwargs):
        return {} if value in ("", b"") else json.loads(value, *args, **kwargs)

    def __getattr__(self, name):
        return getattr(json, name)


def _call_gateway_raw(operation, params):
    """通过公共 run 发起请求，业务层独立管理响应、脱敏和保存。

    仅在本次同步 CLI 调用内替换公共调用器的输出钩子。
    禁止缓存，不让公共 run 的自动落盘覆盖 --no-save 或写入未脱敏数据。
    """
    captured = {}
    transport = shared_api.call_api

    def request(api_path, request_params):
        with patch.object(shared_api, "json", _ResponseJSON()):
            status, body = transport(api_path, request_params)
        if status is None or not 200 <= status < 300:
            body = dict(body) if isinstance(body, dict) else {"details": body}
            body.setdefault("error", f"HTTP {status}" if status is not None else "Connection failed")
            body["transportHttpStatus"] = status
        captured["body"] = body
        # run 的展示要求 object；业务原响应仍由 captured 原样返回。
        rendered = redact(body)
        if not isinstance(rendered, dict):
            rendered = {"response": rendered}
        return status, rendered

    try:
        with patch.object(shared_api, "call_api", request), \
             patch.object(shared_api, "_cache_path", return_value="memory://no-cache"), \
             patch.object(shared_api, "_resolve_output_path", return_value="memory://response"), \
             patch.object(shared_api, "open", side_effect=lambda *a, **k: io.StringIO(), create=True), \
             redirect_stdout(io.StringIO()):
            shared_api.run(
                ENDPOINTS[operation], f"{SLUG}-{operation}",
                [json.dumps(params, ensure_ascii=False), "--inline", "--no-cache"],
            )
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return {"error": f"Invalid JSON response: {exc}"}
    return captured["body"]


def _is_truthy_true(value):
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() == "true"
    return False


def _extract_stores(payload):
    if not isinstance(payload, dict):
        return []
    stores = payload.get("stores")
    if isinstance(stores, list):
        return stores
    data = payload.get("data")
    if isinstance(data, dict) and isinstance(data.get("stores"), list):
        return data["stores"]
    return []


def _has_active_store(payload):
    # 复用公共 errcode 判断（无缓存读写），HTTP 错误已由调用适配层标记。
    # 错误响应即使残留店铺信息，也不能授权后续采购操作。
    if not isinstance(payload, dict) or "error" in payload or not shared_api._is_cacheable(200, payload):
        return False
    for store in _extract_stores(payload):
        if not isinstance(store, dict):
            continue
        status = str(store.get("status", "")).upper()
        if status == "ACTIVE" and not _is_truthy_true(store.get("expired")):
            return True
    return False


def _summarize_authorized_stores(payload):
    summary = []
    for store in _extract_stores(payload):
        if not isinstance(store, dict):
            continue
        summary.append(
            {
                "accountName": store.get("accountName"),
                "status": store.get("status"),
                "expired": store.get("expired"),
            }
        )
    return summary


def _authorization_failure(operation, auth_result):
    return {
        "error": "authorization_required",
        "operation": operation,
        "message": (
            "1688 OAuth authorization is required before this procurement operation. "
            "Run authorized_stores.py to inspect current-user authorization, or authorize_url.py to start OAuth."
        ),
        "authCheck": {
            "endpoint": "authorizedStores",
            "stores": _summarize_authorized_stores(auth_result),
            "raw": redact(auth_result),
        },
    }


def _require_1688_authorization(operation):
    if operation in AUTH_PRECHECK_EXEMPT_OPERATIONS:
        return None
    auth_result = _call_gateway_raw("authorizedStores", {})
    if _has_active_store(auth_result):
        return None
    return _authorization_failure(operation, auth_result)


def call_gateway(operation, params):
    auth_error = _require_1688_authorization(operation)
    if auth_error:
        return auth_error
    return _call_gateway_raw(operation, params)


def _format_iso(ts):
    return time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(ts))


def _session_id(ts):
    env = os.environ.get("SESSION_ID")
    if env:
        return env.strip()
    if "_auto" not in _SESSION_CACHE:
        _SESSION_CACHE["_auto"] = time.strftime("%H%M%S", time.localtime(ts)) + "-" + secrets.token_hex(3)
    return _SESSION_CACHE["_auto"]


def _linkfox_root():
    candidates = []
    acpx = (os.environ.get("ACPX_WORKSPACES") or "").strip()
    if acpx:
        first = acpx.split(os.pathsep)[0].strip()
        if first:
            candidates.append(os.path.join(first, "linkfox"))
    candidates.append(os.path.join(os.getcwd(), "linkfox"))
    candidates.append(os.path.join(os.path.expanduser("~"), "linkfox"))

    tmp_root = os.path.abspath(tempfile.gettempdir())
    for root in candidates:
        try:
            candidate = os.path.abspath(root)
            try:
                in_tmp = os.path.commonpath([candidate, tmp_root]) == tmp_root
            except ValueError:
                in_tmp = False
            if in_tmp:
                continue
            os.makedirs(root, exist_ok=True)
            probe = os.path.join(root, ".write_probe")
            with open(probe, "w", encoding="utf-8") as handle:
                handle.write("")
            os.remove(probe)
            return candidate
        except OSError:
            continue
    raise OSError("No writable linkfox output directory found.")


def save_response(operation, payload):
    ts = time.time()
    date_str = time.strftime("%Y-%m-%d", time.localtime(ts))
    session = _session_id(ts)
    out_dir = os.path.join(_linkfox_root(), date_str, session, "data")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{SLUG}-{operation}-{int(ts * 1_000_000)}.json")
    sanitized = redact(payload)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(sanitized, handle, ensure_ascii=False, indent=2)
    return path, sanitized


def _find_main_list(obj):
    best_path = None
    best_list = []

    def walk(node, path):
        nonlocal best_path, best_list
        if isinstance(node, list):
            if len(node) > len(best_list):
                best_path, best_list = path, node
        elif isinstance(node, dict):
            for key, value in node.items():
                walk(value, f"{path}.{key}" if path else str(key))

    walk(obj, "")
    return best_path, best_list


def summarize(payload):
    if not isinstance(payload, dict):
        print(f"Response type: {type(payload).__name__}")
        return
    print(f"Top-level keys: {list(payload.keys())}")
    for key in ("errcode", "errorCode", "code", "errmsg", "msg", "message", "success", "total", "costToken"):
        if key in payload and isinstance(payload[key], (str, int, float, bool)):
            print(f"  {key}: {payload[key]}")
    list_path, items = _find_main_list(payload)
    if list_path and items:
        print(f"Main list field: `{list_path}` (length={len(items)})")
        print(json.dumps(items[:3], ensure_ascii=False, indent=2))


def run_cli(operation):
    argv = sys.argv[1:]
    if "--help" in argv or "-h" in argv:
        print(f"用法：{os.path.basename(sys.argv[0])} '<JSON 参数>' "
              "[--payload-env ENV_NAME] [--payload-file path.json] "
              "[--inline] [--save] [--no-save] [--no-cache]")
        print("实时请求，不使用响应缓存；高风险操作须先取得用户独立确认。")
        return
    # 兼容公共执行示例；采购业务本来就始终禁用缓存。
    argv = [item for item in argv if item != "--no-cache"]
    inline = False
    force_save = False
    no_save = False
    if "--inline" in argv:
        inline = True
        argv = [item for item in argv if item != "--inline"]
    if "--save" in argv:
        force_save = True
        argv = [item for item in argv if item != "--save"]
    if "--no-save" in argv:
        no_save = True
        argv = [item for item in argv if item != "--no-save"]
    payload = None
    if "--payload-env" in argv:
        index = argv.index("--payload-env")
        try:
            env_name = argv[index + 1]
        except IndexError:
            print("--payload-env requires an environment variable name.", file=sys.stderr)
            sys.exit(1)
        payload = os.environ.get(env_name)
        if payload is None:
            print(f"Environment variable {env_name!r} is not set.", file=sys.stderr)
            sys.exit(1)
        del argv[index:index + 2]
    if "--payload-file" in argv:
        index = argv.index("--payload-file")
        try:
            payload_path = argv[index + 1]
        except IndexError:
            print("--payload-file requires a file path.", file=sys.stderr)
            sys.exit(1)
        with open(payload_path, encoding="utf-8") as handle:
            payload = handle.read()
        del argv[index:index + 2]
    if payload is None and argv:
        payload = argv[0]
    if payload is None:
        print(
            f"Usage: {os.path.basename(sys.argv[0])} '<JSON parameters>' [--inline] "
            "[--payload-env ENV_NAME] [--payload-file path.json]",
            file=sys.stderr,
        )
        sys.exit(1)
    try:
        params = json.loads(payload)
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON parameters: {exc}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(params, dict):
        print("Parameters must be a JSON object.", file=sys.stderr)
        sys.exit(1)

    params = normalize_params(operation, params)
    require_confirmation(operation, params)
    result = call_gateway(operation, params)
    sanitized = redact(result)
    serialized = json.dumps(sanitized, ensure_ascii=False, indent=2)
    serialized_size = len(serialized.encode("utf-8"))
    env_save = os.environ.get("LINKFOX_SKILL_SAVE_RESPONSE", "").strip().lower() in {"1", "true", "yes"}
    env_no_save = os.environ.get("LINKFOX_SKILL_NO_SAVE", "").strip().lower() in {"1", "true", "yes"}
    should_save = (force_save or env_save or serialized_size > SMALL_THRESHOLD) and not (no_save or env_no_save)
    if should_save:
        path, _ = save_response(operation, sanitized)
        print(f"Saved full response: {path} ({serialized_size} bytes)")
    if inline or serialized_size <= SMALL_THRESHOLD:
        print(serialized)
    else:
        summarize(sanitized)
