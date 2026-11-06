"""订单参数兼容、依赖检查及公共调用器适配；不启用响应缓存。"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import tempfile
from pathlib import Path
from typing import Any, Optional
from urllib.parse import quote, urlsplit

import call_api as api

API_BASE_URL = (os.environ.get("LINKFOX_TOOL_GATEWAY") or os.environ.get("SHOPEE_API_BASE_URL") or "https://tool-gateway.linkfox.com").rstrip("/")
STORE_TOKENS_ENDPOINT = f"{API_BASE_URL.rstrip('/')}/shopee/storeTokens"
DEVELOPER_PROXY_ENDPOINT = f"{API_BASE_URL.rstrip('/')}/shopee/developerProxy"

REQUIRED_SKILL = "linkfox-shopee-store-auth"
DEPENDENCY_EXIT_CODE = 42


def ensure_auth_skill_available(caller: str = "orders script") -> None:
    here = Path(__file__).resolve().parent
    checker = here / "check_auth_dependency.py"
    if not checker.exists():
        payload = {
            "missingSkill": REQUIRED_SKILL,
            "reason": f"check_auth_dependency.py not found next to {caller}",
        }
        print(f"DEPENDENCY_MISSING: {json.dumps(payload, ensure_ascii=False)}", file=sys.stderr)
        sys.exit(DEPENDENCY_EXIT_CODE)
    try:
        result = subprocess.run(
            [sys.executable, str(checker)],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except Exception as exc:  # pragma: no cover
        payload = {"missingSkill": REQUIRED_SKILL, "reason": str(exc)}
        print(f"DEPENDENCY_MISSING: {json.dumps(payload, ensure_ascii=False)}", file=sys.stderr)
        sys.exit(DEPENDENCY_EXIT_CODE)
    if result.stderr:
        sys.stderr.write(result.stderr)
        if not result.stderr.endswith("\n"):
            sys.stderr.write("\n")
    if result.returncode != 0:
        sys.exit(DEPENDENCY_EXIT_CODE)


def normal_response(http_status, payload) -> bool:
    """外层 HTTP 2xx 且 errcode 缺失、为空或为 2xx；0/false 不为空。"""
    return (type(http_status) is int and 200 <= http_status < 300
            and isinstance(payload, dict) and api._is_cacheable(200, payload))


def writable_root() -> Path:
    cwd = Path.cwd().resolve()
    if os.name != "nt" and (cwd == Path("/tmp") or Path("/tmp") in cwd.parents):
        raise OSError("本技能禁止将会话响应写入 /tmp，请切换到可写工作目录")
    root = cwd / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    sid = os.environ.get("SESSION_ID", "").strip()
    if sid and (Path(sid).is_absolute() or "/" in sid or chr(92) in sid or sid in (".", "..")):
        raise ValueError("SESSION_ID 必须为单个目录名")
    return root


def call_api(endpoint: str, params: dict, *, transform=None, operation="proxy") -> dict:
    """兼容调用入口；HTTP、落盘和摘要统一委托公共 run。"""
    root = writable_root()  # 请求前检查；禁止回退家目录或临时目录。
    transport = api.call_api
    previous_output = api._resolve_output_path
    previous_root = api._SESSION_CACHE.get("_root")
    previous_gateway = os.environ.get("LINKFOX_TOOL_GATEWAY")
    captured = {}

    def mapped_transport(path, request_params):
        status, proxy = transport(path, request_params)
        result = transform(status, proxy) if transform else proxy
        captured["result"] = result
        return status, result

    parsed = urlsplit(endpoint)
    api_path = parsed.path if parsed.scheme else endpoint
    gateway = endpoint[:-len(parsed.path)] if parsed.scheme and parsed.path else API_BASE_URL
    slug = "linkfox-shopee-store-orders-" + operation
    output_path = None
    try:
        api._SESSION_CACHE["_root"] = str(root)
        os.environ["LINKFOX_TOOL_GATEWAY"] = gateway
        # 在请求前创建本次完整响应文件，具体会话目录不可写时不消耗接口调用。
        output_path = Path(api.resolve_data_path(slug, time.time()))
        with output_path.open("x", encoding="utf-8"):
            pass
        api.call_api = mapped_transport
        api._resolve_output_path = lambda _slug, _ts: str(output_path)
        argv = [json.dumps(params, ensure_ascii=False), "--no-cache"]
        if lf_inline_flag():
            argv.append("--inline")
        api.run(api_path, slug, argv=argv)
        return captured["result"]
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


def resolve_store_tokens(params: dict) -> dict:
    shop_id = params.get("shopId")
    merchant_id = params.get("merchantId")
    if not shop_id and not merchant_id:
        print("Missing required field: shopId OR merchantId", file=sys.stderr)
        sys.exit(1)
    token_req: dict[str, str] = {}
    if shop_id:
        token_req["shopId"] = str(shop_id)
    if merchant_id:
        token_req["merchantId"] = str(merchant_id)
    return call_api(STORE_TOKENS_ENDPOINT, token_req, operation="storeTokens")


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
    transform=None,
    operation="proxy",
) -> dict:
    if not path.startswith("api/v2"):
        print(f"Error: path must start with 'api/v2', got {path!r}", file=sys.stderr)
        sys.exit(1)
    if not shop_id and not merchant_id:
        print("Missing required field: shopId OR merchantId", file=sys.stderr)
        sys.exit(1)
    proxy: dict[str, Any] = {
        "path": path,
        "method": method,
    }
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
    """上游为 200 时提供完整 JSON 解析结果及 response 子对象。"""
    if str(proxy.get("httpStatus") or "").strip() != "200":
        return
    body_raw = proxy.get("body")
    if not body_raw or not str(body_raw).strip():
        out[key] = None
        return
    try:
        parsed = json.loads(body_raw)
    except (TypeError, json.JSONDecodeError):
        out[key] = None
        out[f"{key}Raw"] = body_raw
        return
    out[key] = parsed
    if isinstance(parsed, dict) and parsed.get("response") is not None:
        out[f"{key}Response"] = parsed["response"]


def lf_inline_flag() -> bool:
    """入口脚本的全量输出选项。"""
    return "--inline" in sys.argv[1:]
