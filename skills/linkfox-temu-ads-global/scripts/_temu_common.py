#!/usr/bin/env python3
"""LinkFox Temu 业务参数、认证兼容与公共调用器适配。"""

import json
import os
import sys
import time
import tempfile
from pathlib import Path

import call_api as api

from _temu_token_store import get_token

BASE_URL = (
    os.environ.get("LINKFOX_TOOL_GATEWAY")
    or os.environ.get("TEMU_API_BASE_URL")
    or os.environ.get("STORE_API_BASE_URL", "https://tool-gateway.linkfox.com")
)
BASE_URL = BASE_URL.rstrip("/")
PROXY_URL = f"{BASE_URL}/temu/proxy"
FILE_DOWNLOAD_URL = f"{BASE_URL}/temu/fileDownload"

VALID_SITES = frozenset({"cn", "partner", "us", "global", "eu"})
VALID_MANAGEMENT_TYPES = frozenset({"full-managed", "semi-managed"})

# LinkFox 用户 Token（网关鉴权），勿与 Body 中的 Temu accessToken 混淆
LINKFOX_TOKEN_PARAM_KEYS = ("token", "linkfoxToken", "linkfox_token")

def get_linkfox_token(params=None) -> str:
    """
    LinkFox 用户鉴权 Token，与 linkfox-amazon-store-auth 一致。
    优先级：JSON token / linkfoxToken / linkfox_token > 两个兼容环境变量。
    """
    if params:
        for key in LINKFOX_TOKEN_PARAM_KEYS:
            value = params.get(key)
            if value is not None and str(value).strip():
                return str(value).strip()
    key = os.environ.get("LINKFOX_AGENT_API_KEY") or os.environ.get("LINKFOXAGENT_API_KEY")
    if not key:
        print(
            "LinkFox user Token not configured. Same as linkfox-amazon-store-auth:\n"
            "1. Visit https://skill.linkfox.com/linkfoxskills/guide.htm to obtain your Key\n"
            "2. export LINKFOXAGENT_API_KEY=your-key-here\n"
            "   Or pass \"token\" in the JSON parameters of proxy/fileDownload scripts.",
            file=sys.stderr,
        )
        sys.exit(1)
    return key

def build_gateway_headers(linkfox_token: str) -> dict:
    """网关鉴权：Authorization（全站通用）+ Token（TEMU_API_SPEC 约定）。"""
    return {
        "Authorization": linkfox_token,
        "Token": linkfox_token,
        "Content-Type": "application/json",
        "User-Agent": "LinkFox-Skill/2.0",
        "SESSION_ID": os.environ.get("SESSION_ID", ""),
        "MESSAGE_ID": os.environ.get("MESSAGE_ID", ""),
        "MODE_ID": os.environ.get("MODE_ID", ""),
        "APP_NAME": os.environ.get("APP_NAME", ""),
    }

def load_json_arg(argv: list) -> dict:
    if len(argv) < 2:
        return {}
    try:
        return json.loads(argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid parameter format: {e}", file=sys.stderr)
        sys.exit(1)

def require_text(params: dict, key: str, label=None) -> str:
    value = params.get(key)
    if value is None or not str(value).strip():
        print(f"Error: '{label or key}' is required.", file=sys.stderr)
        sys.exit(1)
    return str(value).strip()

def validate_site(site: str) -> str:
    if site not in VALID_SITES:
        print(
            f"Error: invalid site '{site}'. Must be one of: {', '.join(sorted(VALID_SITES))}",
            file=sys.stderr,
        )
        sys.exit(1)
    return site

def validate_management_type(management_type: str) -> str:
    if management_type not in VALID_MANAGEMENT_TYPES:
        print(
            "Error: invalid managementType. Must be: full-managed, semi-managed",
            file=sys.stderr,
        )
        sys.exit(1)
    return management_type

def call_temu_api(
    url: str,
    body: dict,
    timeout: int = 150,
    linkfox_params=None,
    *,
    response_meta=None,
) -> dict:
    """由公共 run 完成请求与唯一一次落盘，兼容 Temu 双鉴权头和超时。"""
    linkfox_token = get_linkfox_token(linkfox_params)
    root = Path.cwd() / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass

    names = ("call_api", "Request", "urlopen", "get_api_key", "get_api_url", "_resolve_output_path")
    previous = {name: getattr(api, name) for name in names}
    previous_root = api._SESSION_CACHE.get("_root")
    captured = {}
    operation = str(body.get("type") or "fileDownload")
    operation = "".join(c if c.isalnum() or c in "._-" else "_" for c in operation)
    argv = [json.dumps(body, ensure_ascii=False), "--no-cache"]
    if lf_inline_flag():
        argv.append("--inline")

    def request_with_temu_headers(*args, **kwargs):
        kwargs["headers"] = {**kwargs.get("headers", {}), **build_gateway_headers(linkfox_token)}
        return previous["Request"](*args, **kwargs)

    def with_timeout(request, **kwargs):
        # 使用公共调用器持有的 transport，不另实现 HTTP 请求。
        kwargs["timeout"] = timeout
        return previous["urlopen"](request, **kwargs)

    def capture_response(api_path, request_params):
        status, result = previous["call_api"](api_path, request_params)
        if isinstance(result, dict):
            result = {**result, "_httpStatus": status}
        if response_meta is not None:
            response_meta["httpStatus"] = status
            # 复用公共规则：此处只验证 errcode，不启用缓存。
            response_meta["normalResponse"] = (
                status is not None and 200 <= status < 300
                and api._is_cacheable(200, result)
            )
        if url.rstrip("/").endswith("/temu/proxy") and isinstance(result, dict):
            result = parse_nested_body(result)
        captured["result"] = result
        return status, result

    api.Request = request_with_temu_headers
    api.urlopen = with_timeout
    api.get_api_key = lambda: linkfox_token
    api.get_api_url = lambda _path: url
    api.call_api = capture_response
    api._SESSION_CACHE["_root"] = str(root)
    # 连续响应使用微秒时间戳，避免文件互相覆盖。
    api._resolve_output_path = lambda slug, _ts: api.resolve_data_path(slug, time.time())
    try:
        api.run("/temu/fileDownload" if url.rstrip("/").endswith("/temu/fileDownload") else "/temu/proxy",
                f"{SLUG}-{operation}", argv=argv)
        return captured["result"]
    finally:
        for name, value in previous.items():
            setattr(api, name, value)
        if previous_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = previous_root

def is_linkfox_auth_error(result: dict) -> bool:
    msg = " ".join(str(result.get(key) or "") for key in ("message", "error", "errmsg", "details"))
    return "无法识别当前用户" in msg or "重新登录" in msg

def resolve_access_token(params: dict) -> str:
    """Temu 店铺 accessToken：直接传入或从本地 storeKey 读取。"""
    if params.get("accessToken"):
        return str(params["accessToken"]).strip()
    store_key = params.get("storeKey")
    if not store_key:
        print(
            "Error: provide Temu 'accessToken' or 'storeKey' (+ site, managementType).",
            file=sys.stderr,
        )
        sys.exit(1)
    site = validate_site(require_text(params, "site"))
    management_type = validate_management_type(require_text(params, "managementType"))
    token_purpose = str(params.get("tokenPurpose", "default")).strip() or "default"
    token = get_token(str(store_key).strip(), site, management_type, token_purpose)
    if not token:
        print(
            f"Error: no Temu token for storeKey={store_key}, site={site}, "
            f"managementType={management_type}, tokenPurpose={token_purpose}. "
            "Run temu_token_guide.py and save_temu_access_token.py first.",
            file=sys.stderr,
        )
        sys.exit(1)
    return token

def parse_nested_body(result: dict) -> dict:
    """If gateway returns a JSON string in body, parse it into temuBody."""
    body = result.get("body")
    if isinstance(body, str) and body.strip():
        try:
            result["temuBody"] = json.loads(body)
        except json.JSONDecodeError:
            pass
    return result

SLUG = "linkfox-temu-ads-global"


def lf_inline_flag() -> bool:
    """判断是否通过 --inline 请求全量输出。"""
    return "--inline" in sys.argv
