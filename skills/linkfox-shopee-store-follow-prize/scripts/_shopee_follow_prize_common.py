"""Shared helpers for linkfox-shopee-store-follow-prize (storeTokens + developerProxy)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import tempfile
from pathlib import Path
from typing import Any, Optional
from urllib.parse import quote
import call_api as api

API_BASE_URL = os.environ.get("LINKFOX_TOOL_GATEWAY") or os.environ.get("SHOPEE_API_BASE_URL") or "https://tool-gateway.linkfox.com"
STORE_TOKENS_ENDPOINT = f"{API_BASE_URL.rstrip('/')}/shopee/storeTokens"
DEVELOPER_PROXY_ENDPOINT = f"{API_BASE_URL.rstrip('/')}/shopee/developerProxy"

REQUIRED_SKILL = "linkfox-shopee-store-auth"
DEPENDENCY_EXIT_CODE = 42


def ensure_auth_skill_available(caller: str = "follow-prize script") -> None:
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


def get_api_key() -> str:
    """
    获取配置在环境变量的API Key。
    如果获取不到，按 SKILL.md 的 **## 解决认证和算力问题** 处理。
    """
    key = os.environ.get("LINKFOX_AGENT_API_KEY") or os.environ.get("LINKFOXAGENT_API_KEY")
    if not key:
        print(
            "API Key 未配置",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


def _normal_response(status, payload):
    if status is None or not 200 <= status < 300 or not isinstance(payload, dict):
        return False
    code = payload.get("errcode")
    if code is None or (isinstance(code, str) and not code.strip()):
        return True
    if isinstance(code, str):
        code = code.strip()
        if len(code) != 3 or not code.isascii() or not code.isdigit():
            return False
        code = int(code)
    return type(code) in (int, float) and 200 <= code < 300 and code % 1 == 0


def _writable_root():
    root = Path.cwd() / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    return root


def call_api(endpoint: str, params: dict, result_transform=None) -> dict:
    """通过公共 run 传输并输出；不读取或写入响应缓存。"""
    get_api_key()
    root = _writable_root()
    transport = api.call_api
    previous_output = api._resolve_output_path
    previous_root = api._SESSION_CACHE.get("_root")
    previous_gateway = os.environ.get("LINKFOX_TOOL_GATEWAY")
    previous_workspace = os.environ.get("ACPX_WORKSPACES")
    result = {}

    def transformed(path, request):
        nonlocal result
        status, payload = transport(path, request)
        result = result_transform(status, payload) if result_transform else payload
        return status, result

    api.call_api = transformed
    api._SESSION_CACHE["_root"] = str(root)
    os.environ["ACPX_WORKSPACES"] = str(Path.cwd())
    os.environ["LINKFOX_TOOL_GATEWAY"] = API_BASE_URL.rstrip("/")
    try:
        # 请求前检查完整会话目录并预留输出文件，避免请求后才发现无法落盘。
        # 公共 run 以秒取时间；封装使用微秒文件名，避免同秒覆盖。
        output_path = api.resolve_data_path(SLUG, time.time())
        with open(output_path, "x", encoding="utf-8"):
            pass
        api._resolve_output_path = lambda slug, ts: output_path
        argv = [json.dumps(params, ensure_ascii=False), "--no-cache"]
        if lf_inline_flag():
            argv.append("--inline")
        api.run(endpoint.removeprefix(API_BASE_URL.rstrip("/")), SLUG, argv=argv)
    finally:
        api.call_api = transport
        api._resolve_output_path = previous_output
        if previous_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = previous_root
        for key, old in (("LINKFOX_TOOL_GATEWAY", previous_gateway), ("ACPX_WORKSPACES", previous_workspace)):
            if old is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = old
    return result


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
    def with_transport_status(status, payload):
        return {**payload, "transportHttpStatus": status}

    return call_api(STORE_TOKENS_ENDPOINT, token_req, result_transform=with_transport_status)


def developer_proxy_call(
    path: str,
    method: str,
    shop_id: Optional[str] = None,
    merchant_id: Optional[str] = None,
    query_string: Optional[str] = None,
    body: Optional[str] = None,
    content_type: str = "application/json",
    access_token: Optional[str] = None,
    result_transform=None,
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
    return call_api(DEVELOPER_PROXY_ENDPOINT, proxy, result_transform)


def qs_add(parts: list[str], key: str, value: str) -> None:
    parts.append(f"{key}={quote(str(value), safe='')}")


def merge_shopee_body(out: dict, proxy: dict, key: str) -> None:
    try:
        status = int(proxy.get("httpStatus") or 0)
    except (TypeError, ValueError):
        return
    if status != 200:
        return
    body_raw = proxy.get("body")
    if not body_raw or not str(body_raw).strip():
        out[key] = None
        return
    try:
        parsed = json.loads(body_raw)
    except json.JSONDecodeError:
        out[key] = None
        return
    out[key] = parsed
    if isinstance(parsed, dict) and parsed.get("response") is not None:
        out[f"{key}Response"] = parsed["response"]


SLUG = "linkfox-shopee-store-follow-prize"


def lf_inline_flag() -> bool:
    return "--inline" in sys.argv
