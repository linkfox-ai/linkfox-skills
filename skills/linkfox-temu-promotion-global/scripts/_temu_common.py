#!/usr/bin/env python3
"""Shared helpers for LinkFox Temu API skill scripts."""

import json
import os
import sys
import time
import io
from contextlib import redirect_stdout
from pathlib import Path
import tempfile
from unittest.mock import patch

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
LAST_HTTP_STATUS = None

def get_linkfox_token(params=None) -> str:
    """
    LinkFox 用户鉴权 Token，与 linkfox-amazon-store-auth 一致。
    优先级：JSON token / linkfoxToken / linkfox_token，然后 LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY。
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
    """通过公共 run 调用；只在此兼容鉴权、路径和 Temu 解析，不实现 HTTP。"""
    linkfox_token = get_linkfox_token(linkfox_params)
    if url not in (PROXY_URL, FILE_DOWNLOAD_URL):
        raise ValueError("仅允许本技能已定义的 Temu 网关端点")
    api_path = "/temu/proxy" if url == PROXY_URL else "/temu/fileDownload"
    captured = {}
    transport = api.call_api
    request_factory = api.Request
    open_url = api.urlopen
    request_timeout = timeout

    def open_with_timeout(request, timeout=150):
        # Python 辅助函数支持 timeout 参数；HTTP 由公共调用器实现。
        return open_url(request, timeout=request_timeout)

    def request_with_token(*args, **kwargs):
        headers = dict(kwargs.get("headers") or {})
        headers["Token"] = linkfox_token
        kwargs["headers"] = headers
        return request_factory(*args, **kwargs)

    def with_temu_body(path, params):
        global LAST_HTTP_STATUS
        status, result = transport(path, params)
        LAST_HTTP_STATUS = status
        if not isinstance(result, dict):
            # 调用器和 CLI 使用 JSON 对象；保留非对象内容并明确结构错误。
            result = {"error": "网关响应不是 JSON 对象", "body": result}
        else:
            result = dict(result)
        result["transportHttpStatus"] = status
        if api_path == "/temu/proxy":
            parse_nested_body(result)
        captured["result"] = result
        return status, result

    # 在任何请求前检查工作目录可写性，不回退临时目录。
    root = Path.cwd() / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    old_root = api._SESSION_CACHE.get("_root")
    api._SESSION_CACHE["_root"] = str(root)
    argv = [json.dumps(body, ensure_ascii=False), "--no-cache"]
    if lf_inline_flag():
        argv.append("--inline")
    try:
        # patch 仅在此调用有效，异常时同样还原；不修改公共调用器文件。
        with patch.object(api, "get_api_url", lambda _path: url), \
             patch.object(api, "get_api_key", lambda: linkfox_token), \
             patch.object(api, "Request", request_with_token), \
             patch.object(api, "urlopen", open_with_timeout), \
             patch.object(api, "call_api", with_temu_body), \
             patch.object(api, "_resolve_output_path", lambda slug, _ts: api.resolve_data_path(slug, time.time())):
            if emit:
                api.run(api_path, SLUG, argv=argv)
            else:
                # 保留调用函数返回对象的行为；认证探测仍只输出自己的 JSON。
                with redirect_stdout(io.StringIO()):
                    api.run(api_path, SLUG, argv=argv)
    finally:
        if old_root is None:
            api._SESSION_CACHE.pop("_root", None)
        else:
            api._SESSION_CACHE["_root"] = old_root
    return captured["result"]

def is_linkfox_auth_error(result: dict) -> bool:
    if result.get("errcode") in (401, "401"):
        return True
    # 只检查网关消息，不将嵌套 Temu 店铺令牌错误混为 LinkFox 密钥错误。
    messages = "\n".join(
        str(result.get(key) or "") for key in ("message", "error", "errmsg", "msg")
    ).lower()
    return any(marker in messages for marker in (
        "无法识别当前用户", "重新登录", "鉴权失败", "未授权",
        "unauthorized", "authorized error",
    ))

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

# 兼容本地调用者的结果展示入口；不发出网络请求，不启用缓存。
SLUG = "linkfox-temu-promotion-global"


def lf_inline_flag() -> bool:
    """识别业务 CLI 的 --inline 选项。"""
    return "--inline" in sys.argv
