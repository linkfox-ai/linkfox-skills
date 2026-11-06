"""Shopee 物流兼容封装：公共调用器负责 HTTP、落盘与输出，业务入口不缓存响应。"""

from __future__ import annotations

import json
import io
from contextlib import redirect_stdout
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Callable, Optional
from urllib.parse import quote, urlsplit

import call_api as gateway

API_BASE_URL = (os.environ.get("LINKFOX_TOOL_GATEWAY") or os.environ.get("SHOPEE_API_BASE_URL") or "https://tool-gateway.linkfox.com").rstrip("/")
STORE_TOKENS_ENDPOINT = f"{API_BASE_URL}/shopee/storeTokens"
DEVELOPER_PROXY_ENDPOINT = f"{API_BASE_URL}/shopee/developerProxy"
REQUIRED_SKILL = "linkfox-shopee-store-auth"
DEPENDENCY_EXIT_CODE = 42
SLUG = "linkfox-shopee-store-logistics"


def ensure_auth_skill_available(caller: str = "logistics script") -> None:
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


def gateway_ok(http_status, payload) -> bool:
    """依公共响应规则判断外层响应；上游状态另行判断。"""
    if not isinstance(http_status, int) or isinstance(http_status, bool) or not 200 <= http_status < 300 or not isinstance(payload, dict):
        return False
    value = payload.get("errcode")
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


def _output_root() -> Path:
    """仅写当前工作目录，不接受 /tmp。"""
    cwd = Path.cwd()
    if cwd.as_posix() == "/tmp" or cwd.as_posix().startswith("/tmp/"):
        raise OSError("响应禁止写入 /tmp；请切换到任务工作目录")
    root = cwd / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    return root


def call_api(endpoint: str, params: dict, *, transform: Optional[Callable] = None, operation: Optional[str] = None) -> dict:
    """HTTP helper 的兼容入口；所有业务请求均通过 call_api.run。"""
    parts = urlsplit(endpoint)
    base = f"{parts.scheme}://{parts.netloc}" if parts.scheme else API_BASE_URL
    api_path = parts.path if parts.scheme else endpoint
    if parts.scheme:
        for suffix in ("/shopee/developerProxy", "/shopee/storeTokens"):
            if parts.path.endswith(suffix):
                base = endpoint[:-len(suffix)]
                api_path = suffix
                break
    root = _output_root()
    previous_gateway = os.environ.get("LINKFOX_TOOL_GATEWAY")
    previous_root = gateway._SESSION_CACHE.get("_root")
    previous_output = gateway._resolve_output_path
    transport = gateway.call_api
    captured = {}

    def with_business_result(path, request):
        http_status, proxy = transport(path, request)
        result = transform(http_status, proxy) if transform else proxy
        captured["result"] = result
        return http_status, result

    gateway.call_api = with_business_result
    gateway._SESSION_CACHE["_root"] = str(root)
    os.environ["LINKFOX_TOOL_GATEWAY"] = base
    try:
        slug = SLUG + (f"-{operation}" if operation else "")
        # 在真实请求前检查完整会话目录；根目录可写不代表 data 目录可写。
        output_path = gateway.resolve_data_path(slug, time.time())
        with tempfile.TemporaryFile(dir=Path(output_path).parent):
            pass
        gateway._resolve_output_path = lambda _slug, _ts: output_path
        argv = [json.dumps(params, ensure_ascii=False), "--no-cache"]
        if lf_inline_flag():
            argv.append("--inline")
        gateway.run(api_path, slug, argv=argv)
        return captured["result"]
    finally:
        gateway.call_api = transport
        gateway._resolve_output_path = previous_output
        if previous_gateway is None:
            os.environ.pop("LINKFOX_TOOL_GATEWAY", None)
        else:
            os.environ["LINKFOX_TOOL_GATEWAY"] = previous_gateway
        if previous_root is None:
            gateway._SESSION_CACHE.pop("_root", None)
        else:
            gateway._SESSION_CACHE["_root"] = previous_root


def resolve_store_tokens(params: dict) -> dict:
    shop_id, merchant_id = params.get("shopId"), params.get("merchantId")
    if not shop_id and not merchant_id:
        print("Missing required field: shopId OR merchantId", file=sys.stderr)
        raise SystemExit(1)
    request = {}
    if shop_id:
        request["shopId"] = str(shop_id)
    if merchant_id:
        request["merchantId"] = str(merchant_id)
    # helper 仅返回令牌响应，不输出 stdout，避免将令牌直接展示。
    with redirect_stdout(io.StringIO()):
        return call_api(STORE_TOKENS_ENDPOINT, request, operation="storeTokens")


def developer_proxy_call(
    path: str,
    method: str,
    shop_id: Optional[str] = None,
    merchant_id: Optional[str] = None,
    query_string: Optional[str] = None,
    body: Optional[str] = None,
    content_type: str = "application/json",
    access_token: Optional[str] = None,
    *,
    transform: Optional[Callable] = None,
    operation: Optional[str] = None,
) -> dict:
    if not path.startswith("api/v2"):
        print(f"Error: path must start with 'api/v2', got {path!r}", file=sys.stderr)
        raise SystemExit(1)
    if not shop_id and not merchant_id:
        print("Missing required field: shopId OR merchantId", file=sys.stderr)
        raise SystemExit(1)
    proxy: dict[str, Any] = {"path": path, "method": method}
    if shop_id:
        proxy["shopId"] = str(shop_id)
    if merchant_id:
        proxy["merchantId"] = str(merchant_id)
    if access_token:
        proxy["accessToken"] = access_token
    if query_string:
        proxy["queryString"] = query_string
    if body is not None:
        proxy["body"] = body
        proxy["contentType"] = content_type
    return call_api(DEVELOPER_PROXY_ENDPOINT, proxy, transform=transform, operation=operation)


def qs_add(parts: list[str], key: str, value: str) -> None:
    parts.append(f"{key}={quote(str(value), safe='')}")


def merge_shopee_body(out: dict, proxy: dict, key: str) -> None:
    try:
        upstream_status = int(proxy.get("httpStatus") or 0)
    except (TypeError, ValueError):
        return
    if upstream_status != 200:
        return
    body_raw = proxy.get("body")
    if not body_raw or not str(body_raw).strip():
        out[key] = None
        return
    try:
        parsed = json.loads(body_raw)
    except (TypeError, json.JSONDecodeError):
        out[key] = None
        return
    out[key] = parsed
    if isinstance(parsed, dict) and parsed.get("response") is not None:
        out[f"{key}Response"] = parsed["response"]


def lf_inline_flag() -> bool:
    return "--inline" in sys.argv
