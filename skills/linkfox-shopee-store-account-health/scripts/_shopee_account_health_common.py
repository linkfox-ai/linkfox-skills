"""Shopee 账户健康共享封装；HTTP 与持久化统一交给公共调用器。"""

from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Callable, Optional
from urllib.parse import quote, urlsplit

import call_api as api

API_BASE_URL = os.environ.get("LINKFOX_TOOL_GATEWAY") or os.environ.get("SHOPEE_API_BASE_URL") or "https://tool-gateway.linkfox.com"
STORE_TOKENS_ENDPOINT = f"{API_BASE_URL.rstrip('/')}/shopee/storeTokens"
DEVELOPER_PROXY_ENDPOINT = f"{API_BASE_URL.rstrip('/')}/shopee/developerProxy"
REQUIRED_SKILL = "linkfox-shopee-store-auth"
DEPENDENCY_EXIT_CODE = 42
SLUG = "linkfox-shopee-store-account-health"
LF_SMALL_THRESHOLD = api.SMALL_THRESHOLD


def ensure_auth_skill_available(caller: str = "account-health script") -> None:
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


def _summarize_result(result, summarize) -> None:
    """保留公共摘要，并显示加工后嵌套的网关与上游状态。"""
    summarize(result)
    if not isinstance(result, dict):
        return
    if "transportHttpStatus" in result:
        print(f"  transportHttpStatus: {result['transportHttpStatus']}")
    proxy = result.get("developerProxy")
    if isinstance(proxy, dict):
        for field in ("errcode", "errmsg", "httpStatus", "error", "costToken", "costTime"):
            if field in proxy and isinstance(proxy[field], (str, int, float, bool)):
                print(f"  developerProxy.{field}: {str(proxy[field])[:500]}")


@contextlib.contextmanager
def _local_output():
    """请求前检查当前目录，禁止公共调用器回退输出；结束时恢复状态。"""
    root = Path.cwd() / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    old_root = api._SESSION_CACHE.get("_root")
    old_output = api._resolve_output_path
    api._SESSION_CACHE["_root"] = str(root)
    api._resolve_output_path = lambda slug, ts: api.resolve_data_path(slug, time.time())
    try:
        # 根目录可写不代表实际会话目录可写；在发请求前检查最终保存位置。
        _, session_dir = api._ensure_session(time.time())
        data_dir = Path(session_dir) / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryFile(dir=data_dir):
            pass
        yield
    finally:
        api._resolve_output_path = old_output
        if old_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = old_root


def call_api(endpoint: str, params: dict, *, transform: Optional[Callable] = None,
             emit: bool = False, inline: bool = False) -> dict:
    """返回完整结果；通过 run 执行一次请求、加工及完整结果落盘。"""
    path = urlsplit(endpoint).path if "://" in endpoint else endpoint
    if path not in ("/shopee/developerProxy", "/shopee/storeTokens"):
        raise ValueError(f"不支持的 LinkFox 端点: {path}")
    transport = api.call_api
    summarize = api.summarize
    old_gateway = os.environ.get("LINKFOX_TOOL_GATEWAY")
    captured = {}

    def with_result(api_path, request_params):
        status, proxy = transport(api_path, request_params)
        result = transform(status, proxy) if transform else proxy
        captured["result"] = result
        return status, result

    operation = str(params.get("path", "storeTokens")).rsplit("/", 1)[-1]
    try:
        if not old_gateway:
            os.environ["LINKFOX_TOOL_GATEWAY"] = os.environ.get("SHOPEE_API_BASE_URL") or API_BASE_URL
        api.call_api = with_result
        api.summarize = lambda result: _summarize_result(result, summarize)
        argv = [json.dumps(params, ensure_ascii=False), "--no-cache"]
        if inline:
            argv.append("--inline")
        with _local_output():
            if emit:
                api.run(path, f"{SLUG}-{operation}", argv=argv)
            else:
                with contextlib.redirect_stdout(io.StringIO()):
                    api.run(path, f"{SLUG}-{operation}", argv=argv)
        return captured["result"]
    finally:
        api.call_api = transport
        api.summarize = summarize
        if old_gateway is None:
            os.environ.pop("LINKFOX_TOOL_GATEWAY", None)
        else:
            os.environ["LINKFOX_TOOL_GATEWAY"] = old_gateway


def resolve_store_tokens(params: dict) -> dict:
    shop_id, merchant_id = params.get("shopId"), params.get("merchantId")
    if not shop_id and not merchant_id:
        print("Missing required field: shopId OR merchantId", file=sys.stderr)
        raise SystemExit(1)
    token_req = {}
    if shop_id:
        token_req["shopId"] = str(shop_id)
    if merchant_id:
        token_req["merchantId"] = str(merchant_id)

    def with_status(status, response):
        out = dict(response) if isinstance(response, dict) else {"responseBody": response}
        out["transportHttpStatus"] = status
        return out

    return call_api(STORE_TOKENS_ENDPOINT, token_req, transform=with_status)


def developer_proxy_call(path: str, method: str, shop_id: Optional[str] = None,
                         merchant_id: Optional[str] = None, query_string: Optional[str] = None,
                         body: Optional[str] = None, content_type: str = "application/json",
                          *, transform=None,
                         emit: bool = False, inline: bool = False) -> dict:
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
    if query_string:
        proxy["queryString"] = query_string
    if body is not None:
        proxy["body"] = body
        proxy["contentType"] = content_type
    return call_api(DEVELOPER_PROXY_ENDPOINT, proxy, transform=transform, emit=emit, inline=inline)


def qs_add(parts: list[str], key: str, value: str) -> None:
    parts.append(f"{key}={quote(str(value), safe='')}")


def gateway_ok(status, proxy) -> bool:
    if type(status) is not int or not 200 <= status < 300 or not isinstance(proxy, dict):
        return False
    code = proxy.get("errcode")
    if code is None or isinstance(code, str) and not code.strip():
        return True
    if isinstance(code, str):
        code = code.strip()
        if not code.isascii() or not code.isdigit():
            return False
        code = int(code)
    return type(code) in (int, float) and 200 <= code < 300 and code % 1 == 0


def merge_shopee_body(out: dict, proxy: dict, key: str, transport_http_status=200) -> None:
    if not gateway_ok(transport_http_status, proxy):
        return
    try:
        status = int(proxy.get("httpStatus") or 0)
    except (TypeError, ValueError):
        return
    if status != 200:
        return
    body_raw = proxy.get("body")
    try:
        parsed = json.loads(body_raw) if body_raw and str(body_raw).strip() else None
    except (TypeError, json.JSONDecodeError):
        parsed = None
    out[key] = parsed
    if isinstance(parsed, dict) and parsed.get("response") is not None:
        out[f"{key}Response"] = parsed["response"]
