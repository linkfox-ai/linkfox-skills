#!/usr/bin/env python3
"""Shared helpers for LinkFox Temu API skill scripts."""

import json
import os
import sys
import time
import tempfile
import io
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import call_api as api

from _temu_token_store import get_token

BASE_URL = (
    os.environ.get("LINKFOX_TOOL_GATEWAY")
    or os.environ.get("TEMU_API_BASE_URL")
    or os.environ.get("STORE_API_BASE_URL")
    or "https://tool-gateway.linkfox.com"
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
    display: bool = False,
) -> dict:
    """由公共 run 完成 HTTP 和落盘，业务层保留双头鉴权和响应解析。"""
    linkfox_token = get_linkfox_token(linkfox_params)
    root = Path.cwd() / "linkfox"
    # 请求前验证 cwd 可写，不使用公共调用器的家目录/临时目录回退。
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    transport = api.call_api
    request_factory = api.Request
    open_request = api.urlopen
    captured = {}

    def gateway_request(*args, **kwargs):
        headers = dict(kwargs.get("headers") or {})
        headers.update(build_gateway_headers(linkfox_token))
        kwargs["headers"] = headers
        return request_factory(*args, **kwargs)

    def gateway_open(request, **kwargs):
        kwargs["timeout"] = timeout
        return open_request(request, **kwargs)

    def processed_transport(path, params):
        http_status, payload = transport(path, params)
        if not isinstance(payload, dict):
            payload = {"body": payload}
        else:
            payload = dict(payload)
        payload["transportHttpStatus"] = http_status
        if url == PROXY_URL:
            payload = parse_nested_body(payload)
        captured["result"] = payload
        return http_status, payload

    operation = str(body.get("type") or "fileDownload").replace("/", "-").replace("\\", "-")
    argv = [json.dumps(body, ensure_ascii=False), "--no-cache"]
    if lf_inline_flag():
        argv.append("--inline")
    # 所有适配均限于本次同步 CLI 调用，退出时（包括异常）恢复公共模块。
    with patch.object(api, "get_api_key", return_value=linkfox_token), \
         patch.object(api, "get_api_url", return_value=url), \
         patch.object(api, "Request", gateway_request), \
         patch.object(api, "urlopen", gateway_open), \
         patch.object(api, "call_api", processed_transport), \
         patch.object(api, "_linkfox_root", return_value=str(root)), \
         patch.object(api, "_resolve_output_path", lambda slug, ts: api.resolve_data_path(slug, time.time())):
        if display:
            api.run("/temu/fileDownload" if url == FILE_DOWNLOAD_URL else "/temu/proxy",
                    f"{SLUG}-{operation}", argv=argv)
        else:
            # 返回可编程调用所需的 dict；探测脚本自行输出，不污染其 JSON stdout。
            with redirect_stdout(io.StringIO()):
                api.run("/temu/fileDownload" if url == FILE_DOWNLOAD_URL else "/temu/proxy",
                        f"{SLUG}-{operation}", argv=argv)
    return captured["result"]

def is_linkfox_auth_error(result: dict) -> bool:
    if result.get("transportHttpStatus") == 401:
        return True
    msg = " ".join(str(result.get(key) or "") for key in ("message", "error", "errmsg"))
    return "无法识别当前用户" in msg or "重新登录" in msg


def is_gateway_response_normal(result: dict) -> bool:
    """探测结果遵循文档的 HTTP 与 errcode 基础规则，不将 0/false 当作空值。"""
    status = result.get("transportHttpStatus")
    if type(status) is not int or not 200 <= status < 300:
        return False
    code = result.get("errcode")
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

# CLI 标识与输出选项。



SLUG = "linkfox-temu-order-eu"


def lf_inline_flag() -> bool:
    """入口脚本用：从 sys.argv 判断是否 --inline。"""
    return "--inline" in sys.argv

