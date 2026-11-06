"""秒杀请求适配：复用公共调用器，处理认证、选店与响应解析。"""

from __future__ import annotations

from contextlib import nullcontext, redirect_stdout
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from typing import Optional
from urllib.parse import quote

import call_api as api

API_BASE_URL = (
    os.environ.get("LINKFOX_TOOL_GATEWAY")
    or os.environ.get("SHOPEE_API_BASE_URL")
    or "https://tool-gateway.linkfox.com"
).rstrip("/")
STORE_TOKENS_ENDPOINT = f"{API_BASE_URL}/shopee/storeTokens"
DEVELOPER_PROXY_ENDPOINT = f"{API_BASE_URL}/shopee/developerProxy"
REQUIRED_SKILL = "linkfox-shopee-store-auth"
DEPENDENCY_EXIT_CODE = 42
SLUG = "linkfox-shopee-store-shop-flash-sale"


def ensure_auth_skill_available(caller: str = "shop-flash-sale script") -> None:
    checker = Path(__file__).resolve().parent / "check_auth_dependency.py"
    if not checker.exists():
        payload = {"missingSkill": REQUIRED_SKILL,
                   "reason": f"check_auth_dependency.py 不在 {caller} 同目录"}
        print(f"DEPENDENCY_MISSING: {json.dumps(payload, ensure_ascii=False)}", file=sys.stderr)
        raise SystemExit(DEPENDENCY_EXIT_CODE)
    try:
        result = subprocess.run([sys.executable, str(checker)], capture_output=True,
                                text=True, timeout=10)
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


def response_is_normal(http_status, payload) -> bool:
    """按公共规则判断外层 HTTP 与 errcode，避免将 0/false 当作空值。"""
    if not isinstance(http_status, int) or not 200 <= http_status < 300:
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


def call_api(endpoint: str, params: dict, *, result_builder=None,
             display: bool = False, inline: bool = False) -> dict:
    """所有 LinkFox 业务请求经 call_api.run；本技能不读写响应缓存。"""
    cwd = Path.cwd().resolve()
    if os.name != "nt" and (cwd == Path("/tmp") or Path("/tmp") in cwd.parents):
        raise OSError("本技能禁止将会话数据保存到 /tmp")
    root = cwd / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass

    api_path = endpoint
    if endpoint.startswith(API_BASE_URL + "/"):
        api_path = endpoint[len(API_BASE_URL):]
    if not api_path.startswith("/"):
        raise ValueError("接口必须为当前网关的相对路径或完整端点")

    transport = api.call_api
    previous_root = api._SESSION_CACHE.get("_root")
    previous_output = api._resolve_output_path
    previous_gateway = os.environ.get("LINKFOX_TOOL_GATEWAY")
    previous_workspace = os.environ.get("ACPX_WORKSPACES")
    captured = {}

    def with_business_result(path, request_params):
        status, proxy = transport(path, request_params)
        result = result_builder(status, proxy) if result_builder else proxy
        captured["result"] = result
        return status, result

    api.call_api = with_business_result
    api._SESSION_CACHE["_root"] = str(root)
    # 公共文件保持不变；业务层确保同秒多次结果不会互相覆盖。
    api._resolve_output_path = lambda slug, _ts: api.resolve_data_path(slug, time.time())
    os.environ["LINKFOX_TOOL_GATEWAY"] = API_BASE_URL
    os.environ["ACPX_WORKSPACES"] = str(cwd)
    try:
        argv = [json.dumps(params, ensure_ascii=False), "--no-cache"]
        if inline:
            argv.append("--inline")
        with nullcontext() if display else redirect_stdout(io.StringIO()):
            api.run(api_path, SLUG, argv=argv)
        return captured["result"]
    finally:
        api.call_api = transport
        api._resolve_output_path = previous_output
        if previous_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = previous_root
        for key, old in (("LINKFOX_TOOL_GATEWAY", previous_gateway),
                         ("ACPX_WORKSPACES", previous_workspace)):
            if old is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = old


def resolve_store_tokens(params: dict) -> dict:
    """店铺令牌辅助操作；秒杀 CLI 不会自动获取或刷新令牌。"""
    token_req = {key: str(params[key]) for key in ("shopId", "merchantId") if params.get(key)}
    if not token_req:
        print("Missing required field: shopId OR merchantId", file=sys.stderr)
        raise SystemExit(1)
    return call_api(STORE_TOKENS_ENDPOINT, token_req)


def developer_proxy_call(path: str, method: str, shop_id: Optional[str] = None,
                         merchant_id: Optional[str] = None,
                         query_string: Optional[str] = None, body: Optional[str] = None,
                         content_type: str = "application/json",
                         access_token: Optional[str] = None, *, result_builder=None,
                         display: bool = False, inline: bool = False) -> dict:
    if not path.startswith("api/v2"):
        print(f"Error: path must start with 'api/v2', got {path!r}", file=sys.stderr)
        raise SystemExit(1)
    if not shop_id and not merchant_id:
        print("Missing required field: shopId OR merchantId", file=sys.stderr)
        raise SystemExit(1)
    proxy = {"path": path, "method": method}
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
    return call_api(DEVELOPER_PROXY_ENDPOINT, proxy, result_builder=result_builder,
                    display=display, inline=inline)


def qs_add(parts: list[str], key: str, value: str) -> None:
    parts.append(f"{key}={quote(str(value), safe='')}")


def merge_shopee_body(out: dict, proxy: dict, key: str) -> None:
    if not isinstance(proxy, dict) or str(proxy.get("httpStatus")) != "200":
        return
    body_raw = proxy.get("body")
    if body_raw is None or body_raw == "" or (isinstance(body_raw, str) and not body_raw.strip()):
        out[key] = None
        return
    try:
        parsed = json.loads(body_raw) if isinstance(body_raw, str) else body_raw
    except (TypeError, json.JSONDecodeError):
        out[key] = None
        return
    out[key] = parsed
    if isinstance(parsed, dict) and parsed.get("response") is not None:
        out[f"{key}Response"] = parsed["response"]


def lf_inline_flag() -> bool:
    return "--inline" in sys.argv
