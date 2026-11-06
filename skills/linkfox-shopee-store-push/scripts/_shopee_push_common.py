"""Shopee Push 参数兼容及统一调用封装；不缓存响应。"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from contextlib import ExitStack
from pathlib import Path
from typing import Any, Optional
from urllib.parse import quote
from unittest.mock import patch

import call_api as shared

API_BASE_URL = (os.environ.get("LINKFOX_TOOL_GATEWAY") or os.environ.get("SHOPEE_API_BASE_URL") or "https://tool-gateway.linkfox.com").rstrip("/")
STORE_TOKENS_ENDPOINT = f"{API_BASE_URL}/shopee/storeTokens"
DEVELOPER_PROXY_ENDPOINT = f"{API_BASE_URL}/shopee/developerProxy"
REQUIRED_SKILL = "linkfox-shopee-store-auth"
DEPENDENCY_EXIT_CODE = 42
SLUG = "linkfox-shopee-store-push"

def ensure_auth_skill_available(caller: str = "push script") -> None:
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


get_api_key = shared.get_api_key


def response_ok(status, payload):
    """严格执行公共响应码规则，布尔值不作为数值状态。"""
    if type(status) is not int or not 200 <= status < 300 or not isinstance(payload, dict):
        return False
    code = payload.get("errcode")
    if code is None or isinstance(code, str) and not code.strip():
        return True
    if type(code) is bool:
        return False
    if isinstance(code, str):
        code = code.strip()
        if not (len(code) == 3 and code.isascii() and code.isdigit()):
            return False
        code = int(code)
    return type(code) in (int, float) and 200 <= code < 300 and code % 1 == 0


def _output_root():
    # 在任何网关调用前验证当前目录可写，避免公共调用器的目录回退。
    root = Path.cwd() / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    return root


def call_api(endpoint: str, params: dict, *, transform=None, operation="gateway") -> dict:
    """所有 LinkFox 业务请求经公共 run；加工在传输之后、落盘之前执行。"""
    base, api_path = endpoint.rsplit("/shopee/", 1)
    api_path = "/shopee/" + api_path
    root = _output_root()
    transport = shared.call_api
    captured = []
    emitted = []

    def process(path, request):
        status, payload = transport(path, request)
        result = transform(status, payload) if transform else payload
        captured.append(result)
        # 公共 run 需要对象执行输出检查；异常 JSON 完整保留并返回给调用者。
        if not isinstance(result, dict):
            result = {"gatewayResponse": result, "transportHttpStatus": status}
        emitted.append(result)
        return status, result

    previous_root = shared._SESSION_CACHE.get("_root")
    shared._SESSION_CACHE["_root"] = str(root)
    reserved_path = None
    try:
        # 检查实际会话目录和目标文件，不能在远端写入之后才发现无法保存。
        out_path = shared.resolve_data_path(f"{SLUG}-{operation}", time.time())
        with open(out_path, "x", encoding="utf-8"):
            pass
        reserved_path = Path(out_path)
        with ExitStack() as stack:
            stack.enter_context(patch.dict(os.environ, {"LINKFOX_TOOL_GATEWAY": base, "ACPX_WORKSPACES": str(Path.cwd())}))
            stack.enter_context(patch.object(shared, "call_api", process))
            stack.enter_context(patch.object(shared, "_resolve_output_path", lambda slug, ts: out_path))
            argv = [json.dumps(params, ensure_ascii=False), "--no-cache"]
            if lf_inline_flag():
                argv.append("--inline")
            shared.run(api_path, f"{SLUG}-{operation}", argv=argv)
        if Path(out_path).read_text(encoding="utf-8") != json.dumps(emitted[0], ensure_ascii=False, indent=2):
            raise OSError(f"未能保存完整响应：{out_path}；保留当前操作状态，不自动重发请求。")
    finally:
        if reserved_path is not None and reserved_path.exists() and reserved_path.stat().st_size == 0:
            reserved_path.unlink()
        if previous_root is None:
            shared._SESSION_CACHE.pop("_root", None)
        else:
            shared._SESSION_CACHE["_root"] = previous_root
    return captured[0]


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
    return call_api(STORE_TOKENS_ENDPOINT, request, operation="storeTokens")


def developer_proxy_call(path: str, method: str, shop_id: Optional[str] = None,
                         merchant_id: Optional[str] = None, query_string: Optional[str] = None,
                         body: Optional[str] = None, content_type: str = "application/json",
                         access_token: Optional[str] = None, *, transform=None, operation="developerProxy") -> dict:
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
        proxy.update(body=body, contentType=content_type)
    return call_api(DEVELOPER_PROXY_ENDPOINT, proxy, transform=transform, operation=operation)


def qs_add(parts: list[str], key: str, value: str) -> None:
    parts.append(f"{key}={quote(str(value), safe='')}")


def merge_shopee_body(out: dict, proxy: dict, key: str) -> None:
    status = proxy.get("httpStatus")
    if not (type(status) in (int, float) and status == 200 or
            isinstance(status, str) and status.strip() == "200"):
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
    return "--inline" in sys.argv
