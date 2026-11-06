#!/usr/bin/env python3
"""Temu 业务兼容、令牌选择及通用调用器适配。"""

import json
import os
import sys
import time
import tempfile
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

import call_api

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
_LAST_CALL = {}

def get_linkfox_token(params=None) -> str:
    """
    LinkFox 用户鉴权 Token，与 linkfox-amazon-store-auth 一致。
    优先级：JSON token / linkfoxToken / linkfox_token，再取
    LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY。
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
        params = json.loads(argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid parameter format: {e}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(params, dict):
        print("JSON 参数必须为对象。", file=sys.stderr)
        sys.exit(1)
    return params

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
    """通过 call_api.run 调用，发送双鉴权头并禁用响应缓存。"""
    _LAST_CALL.clear()
    linkfox_token = get_linkfox_token(linkfox_params)
    if not url.startswith(BASE_URL + "/"):
        raise ValueError("请求地址必须属于配置的 Temu 网关。")
    api_path = url[len(BASE_URL):]
    if api_path not in ("/temu/proxy", "/temu/fileDownload"):
        raise ValueError("不支持的 Temu 网关路径。")
    # 请求前验证输出位置，禁止回退到其他工作区、家目录或临时目录。
    root = _lf_root()
    slug = SLUG + "-" + str(body.get("type") or "fileDownload").replace(".", "-")
    args = [json.dumps(body, ensure_ascii=False), "--no-cache"]
    if lf_inline_flag():
        args.append("--inline")
    original_request = call_api.Request
    original_urlopen = call_api.urlopen
    original_call = call_api.call_api
    captured = {}

    def compatible_request(*args, **kwargs):
        request = original_request(*args, **kwargs)
        request.add_header("Token", linkfox_token)
        return request

    def compatible_urlopen(request, **kwargs):
        kwargs["timeout"] = timeout
        return original_urlopen(request, **kwargs)

    def capture_response(path, params):
        status, result = original_call(path, params)
        # 公共输出层要求对象；异常形状仍保留原值，供调用方解释。
        if not isinstance(result, dict):
            result = {"_rawGatewayResponse": result}
        result["_linkfoxHttpStatus"] = status
        if api_path == "/temu/proxy":
            parse_nested_body(result)
        captured.update(status=status, result=result)
        return status, result

    output = StringIO()
    with patch.dict(os.environ, {"LINKFOX_AGENT_API_KEY": linkfox_token,
                                 "LINKFOX_TOOL_GATEWAY": BASE_URL}), \
         patch.object(call_api, "Request", compatible_request), \
         patch.object(call_api, "urlopen", compatible_urlopen), \
         patch.object(call_api, "call_api", capture_response), \
         patch.object(call_api, "_linkfox_root", lambda: root), \
         redirect_stdout(output):
        # 提前创建并验证真正的数据目录；仅检查根目录不能阻止请求后才发现落盘失败。
        out_path = call_api.resolve_data_path(slug, time.time())
        with tempfile.NamedTemporaryFile(dir=os.path.dirname(out_path), prefix=".write-probe-", delete=True):
            pass
        with patch.object(call_api, "_resolve_output_path", lambda skill, ts: out_path):
            call_api.run(api_path, slug, argv=args)
    _LAST_CALL.update(captured, output=output.getvalue())
    return captured["result"]

def is_linkfox_auth_error(result: dict) -> bool:
    msg = str(result.get("message") or result.get("errmsg") or result.get("error") or "")
    status = transport_http_status(result)
    errcode = result.get("errcode")
    if isinstance(errcode, str):
        errcode = errcode.strip()
    return (status == 401 or errcode in (401, "401")
            or "无法识别当前用户" in msg or "重新登录" in msg)


def transport_http_status(result):
    """返回当前响应的真实 HTTP 状态，不修改网关响应结构。"""
    return _LAST_CALL.get("status") if result is _LAST_CALL.get("result") else None

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
    if not isinstance(result, dict):
        return result
    body = result.get("body")
    if isinstance(body, str) and body.strip():
        try:
            result["temuBody"] = json.loads(body)
        except json.JSONDecodeError:
            pass
    return result

LF_SMALL_THRESHOLD = call_api.SMALL_THRESHOLD
SLUG = "linkfox-temu-tax-eu"


def _lf_root() -> str:
    root = os.path.abspath(os.path.join(os.getcwd(), "linkfox"))
    os.makedirs(root, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=root, prefix=".write-probe-", delete=True):
        pass
    return root


def emit_result(result, slug=SLUG, inline=False):
    """释放 run 已保存的输出；本地独立结果复用公共落盘与摘要。"""
    if result is _LAST_CALL.get("result") and "output" in _LAST_CALL:
        print(_LAST_CALL.pop("output"), end="")
        return
    serialized = json.dumps(result, ensure_ascii=False, indent=2)
    root = _lf_root()
    with patch.object(call_api, "_linkfox_root", lambda: root):
        out = call_api.resolve_data_path(slug, time.time())
    with open(out, "w", encoding="utf-8") as f:
        f.write(serialized)
    print(f"Saved full response: {out} ({len(serialized)} bytes)")
    if inline or len(serialized.encode("utf-8")) <= LF_SMALL_THRESHOLD:
        print(serialized)
    else:
        call_api.summarize(result)


def lf_inline_flag() -> bool:
    """保留现有 CLI 的 --inline 选项。"""
    return "--inline" in sys.argv
