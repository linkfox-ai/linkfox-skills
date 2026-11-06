"""Shared helpers for linkfox-shopee-store-first-mile (storeTokens + developerProxy)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import tempfile
from pathlib import Path
from typing import Any, Optional
import call_api as api
from urllib.parse import quote, urlsplit

API_BASE_URL = os.environ.get("LINKFOX_TOOL_GATEWAY") or os.environ.get("SHOPEE_API_BASE_URL") or "https://tool-gateway.linkfox.com"
STORE_TOKENS_ENDPOINT = f"{API_BASE_URL.rstrip('/')}/shopee/storeTokens"
DEVELOPER_PROXY_ENDPOINT = f"{API_BASE_URL.rstrip('/')}/shopee/developerProxy"

REQUIRED_SKILL = "linkfox-shopee-store-auth"
DEPENDENCY_EXIT_CODE = 42


def ensure_auth_skill_available(caller: str = "first-mile script") -> None:
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


def _output_file_path(path: str) -> str:
    """Windows 长文件名仍保存到原会话目录，不因 MAX_PATH 误判为不可写。"""
    if os.name != "nt" or len(path) < 260 or path.startswith("\\\\?\\"):
        return path
    absolute = os.path.abspath(path)
    if absolute.startswith("\\\\"):
        return "\\\\?\\UNC\\" + absolute[2:]
    return "\\\\?\\" + absolute


def call_api(endpoint: str, params: dict, *, result_transform=None) -> dict:
    """经公共 run 调用；返回内存原响应，允许业务结果在落盘前加工。"""
    root = Path.cwd() / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    if endpoint == STORE_TOKENS_ENDPOINT:
        api_path = "/shopee/storeTokens"
    elif endpoint == DEVELOPER_PROXY_ENDPOINT:
        api_path = "/shopee/developerProxy"
    else:
        api_path = urlsplit(endpoint).path
    base = endpoint[:-len(api_path)]
    operation = str(params.get("path") or api_path).rsplit("/", 1)[-1]
    transport = api.call_api
    old_root = api._SESSION_CACHE.get("_root")
    old_gateway = os.environ.get("LINKFOX_TOOL_GATEWAY")
    old_output = api._resolve_output_path
    captured = {}

    def collect(path, request_params):
        status, payload = transport(path, request_params)
        captured["payload"] = payload
        if api_path == "/shopee/storeTokens":
            # 店铺令牌仅供内存使用，输出与落盘均使用脱敏字段。
            displayed = {
                "errcode": payload.get("errcode") if isinstance(payload, dict) else None,
                "transportHttpStatus": status,
                "errmsg": "令牌响应仅保留内存；敏感字段不落盘。",
                "tokenResponsePersisted": False,
            }
        else:
            displayed = result_transform(status, payload) if result_transform else payload
        return status, displayed

    api.call_api = collect
    api._SESSION_CACHE["_root"] = str(root)
    os.environ["LINKFOX_TOOL_GATEWAY"] = base
    try:
        slug = f"linkfox-shopee-store-first-mile-{operation}"
        out_path = _output_file_path(api.resolve_data_path(slug, time.time_ns() / 1_000_000_000))
        # 在发请求前确保完整会话路径可写，禁止调用器另选落盘目录。
        with open(out_path, "x", encoding="utf-8"):
            pass
        api._resolve_output_path = lambda _slug, _ts: out_path
        argv = [json.dumps(params, ensure_ascii=False), "--no-cache"]
        if "--inline" in sys.argv[1:]:
            argv.append("--inline")
        api.run(api_path, slug, argv=argv)
    finally:
        api.call_api = transport
        api._resolve_output_path = old_output
        if old_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = old_root
        if old_gateway is None:
            os.environ.pop("LINKFOX_TOOL_GATEWAY", None)
        else:
            os.environ["LINKFOX_TOOL_GATEWAY"] = old_gateway
    return captured["payload"]


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
    return call_api(STORE_TOKENS_ENDPOINT, token_req)


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
    return call_api(DEVELOPER_PROXY_ENDPOINT, proxy, result_transform=result_transform)


def qs_add(parts: list[str], key: str, value: str) -> None:
    parts.append(f"{key}={quote(str(value), safe='')}")


def merge_shopee_body(out: dict, proxy: dict, key: str) -> None:
    status = proxy.get("httpStatus")
    # 异常上游状态不应打断完整网关响应落盘，也不能截断小数后当作成功。
    if isinstance(status, str):
        status = status.strip()
        is_success = status == "200"
    else:
        is_success = type(status) in (int, float) and status == 200
    if not is_success:
        return
    body_raw = proxy.get("body")
    if not body_raw or not str(body_raw).strip():
        out[key] = None
        return
    try:
        parsed = json.loads(body_raw)
    except (ValueError, TypeError):
        out[key] = None
        return
    out[key] = parsed
    if isinstance(parsed, dict) and parsed.get("response") is not None:
        out[f"{key}Response"] = parsed["response"]
