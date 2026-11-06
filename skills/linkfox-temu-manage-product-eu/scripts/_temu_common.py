#!/usr/bin/env python3
"""Temu 认证、业务参数和公共调用器兼容封装。"""

import json
import os
import sys
import time
import tempfile
import contextlib
import io
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
    优先级：请求 JSON 中的 token / linkfoxToken > 环境变量 LINKFOXAGENT_API_KEY。
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
    emit: bool = False,
) -> dict:
    """经公共 run 调用网关，处理认证与嵌套解析，并关闭响应缓存。"""
    linkfox_token = get_linkfox_token(linkfox_params)
    root = Path.cwd() / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    # 公共调用器支持目录回退，本业务要求请求前确认 cwd 可写。
    with tempfile.TemporaryFile(dir=root):
        pass
    path = "/temu/fileDownload" if url.rstrip("/").endswith("/temu/fileDownload") else "/temu/proxy"
    operation = str(body.get("type") or "fileDownload")
    for prefix in ("bg.local.goods.", "temu.local.goods.", "bg.local.", "temu.local."):
        if operation.startswith(prefix):
            operation = operation[len(prefix):]
            break
    # type 不参与路径构造；输出标识保持为文件系统安全的名称。
    operation = "".join(c if c.isalnum() or c in "-_." else "_" for c in operation)
    slug = f"{SLUG}-{operation}"
    transport = api.call_api
    request_factory = api.Request
    opener = api.urlopen
    result_holder = {}

    def with_token_header(*args, **kwargs):
        headers = dict(kwargs.get("headers") or {})
        headers["Token"] = linkfox_token
        kwargs["headers"] = headers
        return request_factory(*args, **kwargs)

    def with_result(api_path, request_params):
        status, result = transport(api_path, request_params)
        if not isinstance(result, dict):
            result = {"body": result}
        result["transportHttpStatus"] = status
        if path == "/temu/proxy":
            parse_nested_body(result)
        result_holder["result"] = result
        return status, result

    # 业务封装设置认证、响应解析与输出路径。
    overrides = {
        "Request": with_token_header,
        "get_api_key": lambda: linkfox_token,
        "get_api_url": lambda _path: url,
        "call_api": with_result,
        "_resolve_output_path": lambda item_slug, _ts: api.resolve_data_path(item_slug, time.time()),
    }
    if timeout != 150:
        # 支持可选超时；请求构造和错误处理由公共 transport 完成。
        overrides["urlopen"] = lambda request, **_kwargs: opener(request, timeout=timeout)
    previous = {key: getattr(api, key) for key in overrides}
    previous_root = api._SESSION_CACHE.get("_root")
    api._SESSION_CACHE["_root"] = str(root.resolve())
    try:
        for key, value in overrides.items():
            setattr(api, key, value)
        argv = [json.dumps(body, ensure_ascii=False), "--no-cache"]
        if lf_inline_flag():
            argv.append("--inline")
        sink = contextlib.nullcontext() if emit else contextlib.redirect_stdout(io.StringIO())
        with sink:
            api.run(path, slug, argv=argv)
        return result_holder["result"]
    finally:
        for key, value in previous.items():
            setattr(api, key, value)
        if previous_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = previous_root


def is_linkfox_auth_error(result: dict) -> bool:
    msg = str(result.get("message") or result.get("errmsg") or result.get("error") or "")
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

SLUG = "linkfox-temu-manage-product-eu"


def lf_inline_flag() -> bool:
    """读取 CLI 的 --inline 选项。"""
    return "--inline" in sys.argv
