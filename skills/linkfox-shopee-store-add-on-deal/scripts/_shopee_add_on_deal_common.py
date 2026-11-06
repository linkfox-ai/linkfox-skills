"""Shared helpers for linkfox-shopee-store-add-on-deal (storeTokens + developerProxy)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Optional
from urllib.parse import quote, urlsplit

import call_api as api

API_BASE_URL = os.environ.get("LINKFOX_TOOL_GATEWAY") or os.environ.get("SHOPEE_API_BASE_URL") or "https://tool-gateway.linkfox.com"
DEVELOPER_PROXY_ENDPOINT = f"{API_BASE_URL.rstrip('/')}/shopee/developerProxy"

REQUIRED_SKILL = "linkfox-shopee-store-auth"
DEPENDENCY_EXIT_CODE = 42


def ensure_auth_skill_available(caller: str = "add-on-deal script") -> None:
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


SLUG = "linkfox-shopee-store-add-on-deal"


def call_api(endpoint: str, params: dict, *, transform=None, slug=SLUG) -> dict:
    """通过公共 run 调用指定网关，并禁用响应缓存。"""
    root = Path.cwd() / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    transport = api.call_api
    previous_root = api._SESSION_CACHE.get("_root")
    previous_gateway = os.environ.get("LINKFOX_TOOL_GATEWAY")
    previous_workspace = os.environ.get("ACPX_WORKSPACES")
    previous_output = api._resolve_output_path
    result = None

    def with_result(api_path, request_params):
        nonlocal result
        status, payload = transport(api_path, request_params)
        result = transform(status, payload) if transform else payload
        return status, result

    parts = urlsplit(endpoint)
    os.environ["LINKFOX_TOOL_GATEWAY"] = endpoint[:-len(parts.path)] if parts.path else endpoint
    os.environ["ACPX_WORKSPACES"] = str(Path.cwd())
    api._SESSION_CACHE["_root"] = str(root)
    api.call_api = with_result
    api._resolve_output_path = lambda name, _ts: api.resolve_data_path(name, time.time())
    try:
        # 根目录可写不代表实际日期/会话目录可写；在店铺写入前检查最终目录。
        _, session_dir = api._ensure_session(time.time())
        data_dir = Path(session_dir) / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryFile(dir=data_dir):
            pass
        argv = [json.dumps(params, ensure_ascii=False), "--no-cache"]
        if "--inline" in sys.argv[1:]:
            argv.append("--inline")
        api.run(parts.path, slug, argv=argv)
    finally:
        api.call_api = transport
        api._resolve_output_path = previous_output
        for name, old in (("LINKFOX_TOOL_GATEWAY", previous_gateway), ("ACPX_WORKSPACES", previous_workspace)):
            if old is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = old
        if previous_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = previous_root
    return result


def developer_proxy_call(
    path: str,
    method: str,
    shop_id: Optional[str] = None,
    merchant_id: Optional[str] = None,
    query_string: Optional[str] = None,
    body: Optional[str] = None,
    content_type: str = "application/json",
    access_token: Optional[str] = None,
    transform=None,
    slug=SLUG,
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
    return call_api(DEVELOPER_PROXY_ENDPOINT, proxy, transform=transform, slug=slug)


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
    except (TypeError, json.JSONDecodeError):
        out[key] = None
        return
    out[key] = parsed
    if isinstance(parsed, dict) and parsed.get("response") is not None:
        out[f"{key}Response"] = parsed["response"]
