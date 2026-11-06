#!/usr/bin/env python3
"""Shared helpers for LinkFox Temu API skill scripts."""

import json
import os
import sys

from _temu_token_store import get_token
from _temu_runtime import invoke, emit_result

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


def load_json_arg(argv: list) -> dict:
    if len(argv) < 2:
        return {}
    try:
        value = json.loads(argv[1])
        if not isinstance(value, dict):
            print("JSON 参数必须是对象", file=sys.stderr)
            sys.exit(1)
        return value
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
) -> dict:
    """使用公共 run 调用网关；保留双请求头与 JSON Key 优先级。"""
    return invoke(url, body, get_linkfox_token(linkfox_params), timeout=timeout)

def is_linkfox_auth_error(result: dict) -> bool:
    msg = str(result.get("message") or result.get("error") or "")
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



def lf_inline_flag() -> bool:
    """读取 CLI 的全量输出选项。"""
    return "--inline" in sys.argv
