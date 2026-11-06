#!/usr/bin/env python3
"""Shared helpers for LinkFox Temu API skill scripts."""

import json
import os
import sys
import time
import secrets
import re
from contextlib import ExitStack, redirect_stdout
from io import StringIO
from unittest.mock import patch

import call_api as _shared_api

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
        params = json.loads(argv[1])
    except json.JSONDecodeError as e:
        print(f"Invalid parameter format: {e}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(params, dict):
        print("参数必须是 JSON 对象。", file=sys.stderr)
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
    """使用公共 run；支持认证兼容及业务输出，不增加响应缓存。"""
    global _LAST_API_OUTPUT
    linkfox_token = get_linkfox_token(linkfox_params)
    # 业务入口只使用本技能的两个网关端点，环境变量优先级由 BASE_URL 确定。
    if url not in (PROXY_URL, FILE_DOWNLOAD_URL):
        raise ValueError("Unsupported Temu gateway URL")
    api_path = "/temu/proxy" if url == PROXY_URL else "/temu/fileDownload"
    operation = re.sub(r"[^A-Za-z0-9_-]+", "-", str(body.get("type") or "fileDownload")).strip("-") or "proxy"
    slug = f"{SLUG}-{operation}"
    _lf_root()  # 在网络请求前验证 cwd 可写，不回退到其他目录。
    original_request = _shared_api.Request
    original_call = _shared_api.call_api
    captured = {}

    def request_with_legacy_headers(*args, **kwargs):
        headers = dict(kwargs.get("headers") or {})
        headers.update(build_gateway_headers(linkfox_token))
        kwargs["headers"] = headers
        return original_request(*args, **kwargs)

    def call_and_process(path, params):
        status, result = original_call(path, params)
        if not isinstance(result, dict):
            result = {"gatewayResponse": result}
        result["transportHttpStatus"] = status
        if api_path == "/temu/proxy":
            parse_nested_body(result)
        captured["result"] = result
        return status, result

    # 公共调用器超时固定为 150 秒；业务入口也均使用 150 秒。
    # 为保留 helper 的 timeout 可选参数，在公共 urlopen 绑定层调整该实参，
    # 不实现新的 HTTP transport。
    original_open = _shared_api.urlopen

    def open_with_timeout(request, timeout=150):
        return original_open(request, timeout=request_timeout)

    request_timeout = timeout
    output = StringIO()
    argv = [json.dumps(body, ensure_ascii=False), "--no-cache"]
    if lf_inline_flag():
        argv.append("--inline")
    with ExitStack() as stack:
        stack.enter_context(patch.object(_shared_api, "get_api_key", return_value=linkfox_token))
        stack.enter_context(patch.object(_shared_api, "get_api_url", return_value=url))
        stack.enter_context(patch.object(_shared_api, "Request", request_with_legacy_headers))
        stack.enter_context(patch.object(_shared_api, "urlopen", open_with_timeout))
        stack.enter_context(patch.object(_shared_api, "call_api", call_and_process))
        stack.enter_context(patch.object(_shared_api, "_linkfox_root", _lf_root))
        stack.enter_context(patch.object(
            _shared_api, "_resolve_output_path",
            lambda output_slug, ts: _shared_api.resolve_data_path(output_slug, time.time()),
        ))
        stack.enter_context(redirect_stdout(output))
        _shared_api.run(api_path, slug, argv=argv)
    result = captured["result"]
    _LAST_API_OUTPUT = (result, output.getvalue())
    return result

def is_linkfox_auth_error(result: dict) -> bool:
    msg = " ".join(str(result.get(key) or "") for key in ("message", "error", "errmsg", "msg"))
    return (
        "无法识别当前用户" in msg
        or "重新登录" in msg
        or "unauthorized" in msg.lower()
        or result.get("transportHttpStatus") == 401
        or result.get("errcode") in (401, "401")
    )

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

def is_empty_or_2xx(value) -> bool:
    """公共规则仅用于外层 errcode，不用于 Temu 网关业务 code。"""
    if value is None or (isinstance(value, str) and not value.strip()):
        return True
    if isinstance(value, str):
        value = value.strip()
        if not (len(value) == 3 and value.isascii() and value.isdigit()):
            return False
        value = int(value)
    return type(value) in (int, float) and 200 <= value < 300 and value % 1 == 0


def parse_nested_body(result: dict) -> dict:
    """外层正常且没有已定义的网关错误时解析；解析不代表业务成功。"""
    if "transportHttpStatus" in result:
        status = result["transportHttpStatus"]
        if type(status) is not int or not 200 <= status < 300:
            return result
    if not is_empty_or_2xx(result.get("errcode")):
        return result
    # 网关错误码只明确列出 code=1002/1003；不为 code 发明成功枚举。
    # 其他 code 保留原值并解析 body 供诊断，仍须核对 Temu success/errorCode。
    if str(result.get("code", "")).strip() in ("1002", "1003"):
        return result
    body = result.get("body")
    if isinstance(body, str) and body.strip():
        try:
            result["temuBody"] = json.loads(body)
        except json.JSONDecodeError:
            pass
    return result

# ===== LinkFox 统一输出层（落盘 + 摘要，无缓存）=====
# emit_result 支持本地结果输出；网络响应由公共 run 保存一次。

import time as _lf_time
import secrets as _lf_secrets

LF_SMALL_THRESHOLD = 8000
_LF_SESSION_CACHE: dict = {}
_LAST_API_OUTPUT = None

SLUG = "linkfox-temu-ads-us"


def _lf_root() -> str:
    root = os.path.abspath(os.path.join(os.getcwd(), "linkfox"))
    os.makedirs(root, exist_ok=True)
    probe = os.path.join(root, f".write-probe-{secrets.token_hex(6)}")
    with open(probe, "x", encoding="utf-8"):
        pass
    os.remove(probe)
    return root


def _lf_iso(ts: float) -> str:
    return _lf_time.strftime("%Y-%m-%dT%H:%M:%S%z", _lf_time.localtime(ts))


def _lf_session_id(ts: float) -> str:
    env = os.environ.get("SESSION_ID")
    if env:
        return env.strip()
    if "_auto" not in _LF_SESSION_CACHE:
        _LF_SESSION_CACHE["_auto"] = (
            _lf_time.strftime("%H%M%S", _lf_time.localtime(ts)) + "-" + _lf_secrets.token_hex(3)
        )
    return _LF_SESSION_CACHE["_auto"]


def _lf_find_main_list(obj):
    best = (None, None, -1)

    def walk(node, path):
        nonlocal best
        if isinstance(node, list):
            if len(node) > best[2]:
                best = (path, node, len(node))
        elif isinstance(node, dict):
            for k, v in node.items():
                walk(v, f"{path}.{k}" if path else k)

    walk(obj, "")
    return best[0], best[1]


def _lf_summarize(result) -> None:
    if not isinstance(result, dict):
        print(f"Response type: {type(result).__name__}")
        print(json.dumps(result, ensure_ascii=False)[:500])
        return
    print(f"Top-level keys: {list(result.keys())}")
    for k in ("errcode", "errorCode", "code", "errmsg", "msg",
              "total", "totalCount", "count", "currentPage", "perPage",
              "costToken", "costTime", "success"):
        if k in result:
            v = result[k]
            if isinstance(v, (int, float, bool, str)):
                print(f"  {k}: {v}")
    list_path, main_list = _lf_find_main_list(result)
    if list_path is not None and main_list:
        print(f"\nMain list field: `{list_path}` (length={len(main_list)})")
        sample = main_list[:3]
        print(f"Sample (first {len(sample)} of {len(main_list)}):")
        print(json.dumps(sample, indent=2, ensure_ascii=False))


def _lf_ensure_meta(root: str, session_dir: str, date_str: str, sid: str, ts: float) -> None:
    meta_path = os.path.join(session_dir, "_meta.json")
    if os.path.exists(meta_path):
        return
    meta = {
        "session_id": sid,
        "date": date_str,
        "started_at": _lf_iso(ts),
        "skills_called": [],
        "deliverables": [],
        "data_files": [],
        "media_files": [],
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    try:
        with open(os.path.join(root, "index.jsonl"), "a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "session_id": sid,
                        "date": date_str,
                        "path": os.path.relpath(session_dir, root),
                        "started_at": _lf_iso(ts),
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
    except OSError:
        pass


def _lf_update_meta(session_dir: str, *, skill: str, file_rel: str, ts: float) -> None:
    meta_path = os.path.join(session_dir, "_meta.json")
    try:
        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)
    except (OSError, json.JSONDecodeError):
        return
    if skill and skill not in meta.setdefault("skills_called", []):
        meta["skills_called"].append(skill)
    files = meta.setdefault("data_files", [])
    if file_rel not in files:
        files.append(file_rel)
    meta["last_used_at"] = _lf_iso(ts)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


def emit_result(result, slug=SLUG, inline=False):
    """落盘完整响应到 linkfox/<date>/<session>/data/<slug>-<ts>.json；大响应只打印摘要。无缓存。"""
    global _LAST_API_OUTPUT
    if _LAST_API_OUTPUT is not None and _LAST_API_OUTPUT[0] is result:
        # 公共 run 已保存加工后的最终响应，只转发其输出，避免重复文件。
        print(_LAST_API_OUTPUT[1], end="")
        _LAST_API_OUTPUT = None
        return
    serialized = json.dumps(result, ensure_ascii=False, indent=2)
    ts = _lf_time.time()
    date_str = _lf_time.strftime("%Y-%m-%d", _lf_time.localtime(ts))
    sid = _lf_session_id(ts)
    root = _lf_root()
    session_dir = os.path.join(root, date_str, sid)
    os.makedirs(session_dir, exist_ok=True)
    _lf_ensure_meta(root, session_dir, date_str, sid, ts)
    data_dir = os.path.join(session_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    out = os.path.join(data_dir, f"{slug}-{int(ts * 1_000_000)}.json")
    try:
        with open(out, "w", encoding="utf-8") as f:
            f.write(serialized)
        print(f"Saved full response: {out} ({len(serialized)} bytes)")
    except OSError as e:
        print(f"Failed to save to {out}: {e}", file=sys.stderr)
    _lf_update_meta(session_dir, skill=slug, file_rel=os.path.relpath(out, session_dir), ts=ts)
    if inline or len(serialized.encode("utf-8")) <= LF_SMALL_THRESHOLD:
        print(serialized)
    else:
        _lf_summarize(result)


def lf_inline_flag() -> bool:
    """入口脚本用：从 sys.argv 判断是否 --inline。"""
    return "--inline" in sys.argv
