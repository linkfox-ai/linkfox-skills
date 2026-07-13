#!/usr/bin/env python3
"""Common CLI helpers for linkfox-1688-procurement scripts."""

import json
import os
import secrets
import sys
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


SLUG = "linkfox-1688-procurement"
TIMEOUT_SECONDS = 120
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
}

CONFIRM_FIELDS = {
    "createOrder": "confirmCreateOrder",
    "paymentUrl": "confirmGetPaymentUrl",
    "confirmReceive": "confirmReceive",
    "cancelOrder": "confirmCancel",
}

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
}

_SESSION_CACHE = {}


def get_api_base():
    return (os.environ.get("LINKFOX_TOOL_GATEWAY") or "https://tool-gateway.linkfox.com").rstrip("/")


def get_api_key():
    """
    获取配置在环境变量的API Key。
    如果获取不到，按 SKILL.md 的 **## 解决认证和积分问题** 处理。
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


def redact(value):
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
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


def _call_gateway_raw(operation, params):
    path = ENDPOINTS[operation]
    data = json.dumps(params, ensure_ascii=False).encode("utf-8")
    headers = {
        "Authorization": get_api_key(),
        "Content-Type": "application/json; charset=utf-8",
        "User-Agent": "LinkFox-Skill/2.0",
        "SESSION_ID": os.environ.get("SESSION_ID", ""),
        "MODE_ID": os.environ.get("MODE_ID", ""),
        "APP_NAME": os.environ.get("APP_NAME", ""),
    }
    req = Request(get_api_base() + path, data=data, headers=headers, method="POST")
    try:
        with urlopen(req, timeout=TIMEOUT_SECONDS) as response:
            body = response.read().decode("utf-8")
            return json.loads(body) if body else {}
    except HTTPError as exc:
        body = exc.read().decode("utf-8") if exc.fp else ""
        try:
            parsed = json.loads(body) if body else {}
        except json.JSONDecodeError:
            parsed = {"details": body}
        parsed.setdefault("error", f"HTTP {exc.code}: {exc.reason}")
        return parsed
    except URLError as exc:
        return {"error": f"Connection failed: {exc.reason}"}
    except json.JSONDecodeError as exc:
        return {"error": f"Invalid JSON response: {exc}"}


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
                "tokenExpiresAt": store.get("tokenExpiresAt"),
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
