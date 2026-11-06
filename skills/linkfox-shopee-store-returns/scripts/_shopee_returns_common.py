"""退货退款的依赖、参数及输出兼容层；LinkFox HTTP 统一交给 call_api.run。"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Callable, Optional
from urllib.parse import quote

import call_api as api

API_BASE_URL = (os.environ.get("LINKFOX_TOOL_GATEWAY") or os.environ.get("SHOPEE_API_BASE_URL") or "https://tool-gateway.linkfox.com").rstrip("/")
STORE_TOKENS_ENDPOINT = f"{API_BASE_URL}/shopee/storeTokens"
DEVELOPER_PROXY_ENDPOINT = f"{API_BASE_URL}/shopee/developerProxy"
REQUIRED_SKILL = "linkfox-shopee-store-auth"
DEPENDENCY_EXIT_CODE = 42
SLUG = "linkfox-shopee-store-returns"
LF_SMALL_THRESHOLD = api.SMALL_THRESHOLD


def ensure_auth_skill_available(caller: str = "退货脚本") -> None:
    checker = Path(__file__).resolve().parent / "check_auth_dependency.py"
    if not checker.exists():
        payload = {"missingSkill": REQUIRED_SKILL, "reason": f"{caller} 同目录缺少 check_auth_dependency.py"}
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


def _writable_root() -> Path:
    """在请求前确认 cwd 可写，防止公共调用器回退到其他目录。"""
    root = Path.cwd() / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    return root


def call_api(endpoint: str, params: dict, *, transform: Optional[Callable] = None, slug: str = SLUG) -> dict:
    """保留返回对象，同时由公共 run 保存并打印完整业务结果；始终无缓存。"""
    root = _writable_root()
    transport = api.call_api
    old_output_path = api._resolve_output_path
    old_root = api._SESSION_CACHE.get("_root")
    old_gateway = os.environ.get("LINKFOX_TOOL_GATEWAY")
    old_workspace = os.environ.get("ACPX_WORKSPACES")
    captured: dict[str, Any] = {}

    def with_result(api_path, request_params):
        status, payload = transport(api_path, request_params)
        result = transform(status, payload) if transform else payload
        if not isinstance(result, dict):
            result = {"rawResponse": result}
        captured["result"] = result
        return status, result

    # 接受完整端点形式，网络请求全部通过公共 transport。
    if endpoint.startswith("/"):
        api_path = endpoint
        gateway = old_gateway or os.environ.get("SHOPEE_API_BASE_URL") or API_BASE_URL
    else:
        gateway, suffix = endpoint.split("/shopee/", 1)
        api_path = "/shopee/" + suffix
    os.environ["LINKFOX_TOOL_GATEWAY"] = gateway.rstrip("/")
    os.environ["ACPX_WORKSPACES"] = str(Path.cwd())
    api._SESSION_CACHE["_root"] = str(root)
    api.call_api = with_result
    # 适配层用微秒路径避免同秒调用相互覆盖。
    api._resolve_output_path = lambda slug, _ts: api.resolve_data_path(slug, time.time())
    try:
        argv = [json.dumps(params, ensure_ascii=False), "--no-cache"]
        if lf_inline_flag():
            argv.append("--inline")
        api.run(api_path, slug, argv=argv)
    finally:
        api.call_api = transport
        api._resolve_output_path = old_output_path
        for name, previous in (("LINKFOX_TOOL_GATEWAY", old_gateway), ("ACPX_WORKSPACES", old_workspace)):
            if previous is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = previous
        if old_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = old_root
    return captured["result"]


def resolve_store_tokens(params: dict) -> dict:
    """店铺授权状态查询辅助函数；主流程不调用。"""
    shop_id, merchant_id = params.get("shopId"), params.get("merchantId")
    if not shop_id and not merchant_id:
        print("缺少必填字段：shopId 或 merchantId", file=sys.stderr)
        raise SystemExit(1)
    token_req = {}
    if shop_id:
        token_req["shopId"] = str(shop_id)
    if merchant_id:
        token_req["merchantId"] = str(merchant_id)
    return call_api(STORE_TOKENS_ENDPOINT, token_req, slug=f"{SLUG}-store-tokens")


def developer_proxy_call(
    path: str, method: str, shop_id: Optional[str] = None,
    merchant_id: Optional[str] = None, query_string: Optional[str] = None,
    body: Optional[str] = None, content_type: str = "application/json",
    access_token: Optional[str] = None, *, transform: Optional[Callable] = None,
    slug: str = SLUG,
) -> dict:
    if not path.startswith("api/v2"):
        print(f"path 必须以 api/v2 开始，实际为 {path!r}", file=sys.stderr)
        raise SystemExit(1)
    if not shop_id and not merchant_id:
        print("缺少必填字段：shopId 或 merchantId", file=sys.stderr)
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
    return call_api(DEVELOPER_PROXY_ENDPOINT, proxy, transform=transform, slug=slug)


def qs_add(parts: list[str], key: str, value: str) -> None:
    parts.append(f"{key}={quote(str(value), safe='')}")


def gateway_ok(status, proxy) -> bool:
    """只判断外层 HTTP 与 errcode，Shopee 状态另行判断。"""
    if type(status) is not int or not 200 <= status <= 299 or not isinstance(proxy, dict):
        return False
    code = proxy.get("errcode")
    if code is None:
        return True
    if isinstance(code, str):
        code = code.strip()
        if not code:
            return True
        if len(code) != 3 or not code.isascii() or not code.isdigit():
            return False
        code = int(code)
    return type(code) in (int, float) and 200 <= code <= 299 and code % 1 == 0


def merge_shopee_body(out: dict, proxy: dict, key: str) -> None:
    try:
        if int(proxy.get("httpStatus") or 0) != 200:
            return
    except (TypeError, ValueError):
        return
    raw = proxy.get("body")
    try:
        parsed = json.loads(raw) if raw and str(raw).strip() else None
    except (TypeError, json.JSONDecodeError):
        parsed = None
    out[key] = parsed
    if isinstance(parsed, dict) and parsed.get("response") is not None:
        out[f"{key}Response"] = parsed["response"]


def lf_inline_flag() -> bool:
    return "--inline" in sys.argv[1:]
