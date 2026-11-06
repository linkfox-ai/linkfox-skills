"""直播封装与公共 run 适配；不读取或保存响应缓存。"""
from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from typing import Any, Optional
from urllib.parse import quote

import call_api as api

API_BASE_URL = os.environ.get("LINKFOX_TOOL_GATEWAY") or os.environ.get("SHOPEE_API_BASE_URL") or "https://tool-gateway.linkfox.com"
STORE_TOKENS_ENDPOINT = f"{API_BASE_URL.rstrip('/')}/shopee/storeTokens"
DEVELOPER_PROXY_ENDPOINT = f"{API_BASE_URL.rstrip('/')}/shopee/developerProxy"
REQUIRED_SKILL = "linkfox-shopee-store-auth"
DEPENDENCY_EXIT_CODE = 42
SLUG = "linkfox-shopee-store-livestream"

def ensure_auth_skill_available(caller: str = "livestream script") -> None:
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


def _output_root() -> Path:
    """请求前检查 cwd 可写，不使用其他目录兜底。"""
    cwd = Path.cwd().resolve()
    temp_root = Path(tempfile.gettempdir()).resolve()
    if cwd == temp_root or temp_root in cwd.parents:
        raise OSError("当前目录是临时目录；请切换到可写项目目录")
    root = cwd / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    if root.resolve().parent != cwd:
        raise OSError("linkfox 输出目录必须位于当前工作目录")
    with tempfile.TemporaryFile(dir=root):
        pass
    return root


def is_normal_response(http_status, payload) -> bool:
    """按公共规则检查网关 HTTP 与 errcode；0 和 false 不为空。"""
    if type(http_status) is not int or not 200 <= http_status < 300:
        return False
    if not isinstance(payload, dict):
        return False
    code = payload.get("errcode")
    if code is None:
        return True
    if isinstance(code, str):
        code = code.strip()
        if not code:
            return True
        if len(code) != 3 or not code.isascii() or not code.isdigit():
            return False
        code = int(code)
    return type(code) in (int, float) and 200 <= code < 300 and code % 1 == 0


def call_api(endpoint: str, params: dict, *, result_builder=None, emit=False, inline=False, operation=None) -> dict:
    """公共 run 负责唯一 HTTP 和落盘；令牌原值只在内存返回。"""
    root = _output_root()
    base, slash, name = endpoint.rpartition("/shopee/")
    if not slash or not name:
        raise ValueError("仅支持 Shopee 网关端点")
    path = "/shopee/" + name
    # 在设置临时适配器前序列化；Python 兼容调用的无效参数也不能污染后续调用。
    argv = [json.dumps(params, ensure_ascii=False), "--no-cache"]
    if inline:
        argv.append("--inline")
    is_tokens = path == "/shopee/storeTokens"
    captured = {}
    transport = api.call_api
    output_path = api._resolve_output_path
    old_root = api._SESSION_CACHE.get("_root")
    old_gateway = os.environ.get("LINKFOX_TOOL_GATEWAY")

    def transform(api_path, request_params):
        status, raw = transport(api_path, request_params)
        result = result_builder(status, raw) if result_builder else raw
        captured["result"] = result
        if is_tokens:
            return status, {"redacted": True, "transportHttpStatus": status}
        return status, result

    try:
        api._SESSION_CACHE["_root"] = str(root)
        os.environ["LINKFOX_TOOL_GATEWAY"] = base
        api.call_api = transform
        api._resolve_output_path = lambda slug, _ts: api.resolve_data_path(slug, time.time())
        # 输出根可写并不代表既有会话的 data 目录可写；在请求前验证实际目录。
        _, session_dir = api._ensure_session(time.time())
        data_dir = Path(session_dir) / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryFile(dir=data_dir):
            pass
        if emit and not is_tokens:
            api.run(path, f"{SLUG}-{operation or name}", argv=argv)
        else:
            with redirect_stdout(io.StringIO()):
                api.run(path, f"{SLUG}-{operation or name}", argv=argv)
    finally:
        api.call_api = transport
        api._resolve_output_path = output_path
        if old_gateway is None:
            os.environ.pop("LINKFOX_TOOL_GATEWAY", None)
        else:
            os.environ["LINKFOX_TOOL_GATEWAY"] = old_gateway
        if old_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = old_root
    return captured["result"]


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
    *, result_builder=None, emit=False, inline=False, operation=None,
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
    return call_api(
        DEVELOPER_PROXY_ENDPOINT, proxy, result_builder=result_builder,
        emit=emit, inline=inline, operation=operation,
    )


def qs_add(parts: list[str], key: str, value: str) -> None:
    parts.append(f"{key}={quote(str(value), safe='')}")


def merge_shopee_body(out: dict, proxy: dict, key: str) -> None:
    try:
        upstream_status = int(proxy.get("httpStatus") or 0)
    except (ValueError, TypeError):
        return
    if upstream_status != 200:
        return
    raw = proxy.get("body")
    if not raw or not str(raw).strip():
        out[key] = None
        return
    try:
        parsed = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        out[key] = None
        out[f"{key}Raw"] = raw
        return
    out[key] = parsed
    if isinstance(parsed, dict) and parsed.get("response") is not None:
        out[f"{key}Response"] = parsed["response"]


