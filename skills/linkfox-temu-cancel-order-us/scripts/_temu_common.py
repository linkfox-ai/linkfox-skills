#!/usr/bin/env python3
"""Shared helpers for LinkFox Temu API skill scripts."""

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
    优先级：JSON token / linkfoxToken / linkfox_token，随后依次使用
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

class _GatewayResult(dict):
    """沿用 dict 调用契约，暂存公共 run 的输出以供命令行入口展示。"""


def call_temu_api(url: str, body: dict, timeout: int = 150, linkfox_params=None) -> dict:
    """交给公共 run 请求和落盘，在业务封装中适配双请求头鉴权与响应加工。"""
    linkfox_token = get_linkfox_token(linkfox_params)
    root = _lf_root()  # 网络请求前确认 cwd 可写，不采用公共调用器的回退目录。
    transport = api.call_api
    request_factory = api.Request
    opener = api.urlopen
    captured = {}

    def request_with_token(*args, **kwargs):
        headers = dict(kwargs.get("headers") or {})
        headers["Token"] = linkfox_token
        kwargs["headers"] = headers
        return request_factory(*args, **kwargs)

    def with_business_result(api_path, request_params):
        status, result = transport(api_path, request_params)
        # 公共 run 按对象访问响应；异常 JSON 值保留在业务错误中，避免落盘前崩溃。
        if not isinstance(result, dict):
            result = {"error": "Temu 网关返回了非对象 JSON", "gatewayResponse": result}
        # 本地传输状态随响应落盘，不能只留在 Python 对象属性中。
        result["_http_status"] = status
        if url == PROXY_URL:
            result = parse_nested_body(result)
        captured["result"] = result
        captured["http_status"] = status
        return status, result

    previous = {name: getattr(api, name) for name in (
        "get_api_key", "get_api_url", "Request", "urlopen", "call_api",
        "_linkfox_root", "_resolve_output_path",
    )}
    api.get_api_key = lambda: linkfox_token
    api.get_api_url = lambda _path: url
    api.Request = request_with_token
    call_timeout = timeout
    api.urlopen = lambda req, timeout=150: opener(req, timeout=call_timeout)
    api.call_api = with_business_result
    api._linkfox_root = lambda: root
    api._resolve_output_path = lambda slug, _ts: api.resolve_data_path(slug, time.time())
    output = io.StringIO()
    try:
        argv = [json.dumps(body, ensure_ascii=False), "--no-cache"]
        if lf_inline_flag():
            argv.append("--inline")
        with contextlib.redirect_stdout(output):
            api.run("/temu/fileDownload" if url == FILE_DOWNLOAD_URL else "/temu/proxy", SLUG, argv=argv)
    finally:
        for name, value in previous.items():
            setattr(api, name, value)
    result = _GatewayResult(captured["result"])
    status_label = captured["http_status"] if captured["http_status"] is not None else "unavailable"
    result.cli_output = f"HTTP status: {status_label}\n" + output.getvalue()
    result.http_status = captured["http_status"]
    return result


def is_linkfox_auth_error(result: dict) -> bool:
    if getattr(result, "http_status", None) == 403 or str(result.get("errcode", "")).strip() == "403":
        return False  # 无权限不引导为重新配置密钥。
    messages = " ".join(str(result.get(k) or "") for k in ("message", "error", "errmsg"))
    return (
        getattr(result, "http_status", None) == 401
        or str(result.get("errcode", "")).strip() == "401"
        or any(part in messages.lower() for part in (
            "无法识别当前用户", "重新登录", "authorized error", "unauthorized", "鉴权失败", "未授权",
        ))
    )


def is_gateway_response_normal(result: dict) -> bool:
    """认证探测按公共 HTTP/errcode 规则判断，不把连接失败当成令牌有效。"""
    status = getattr(result, "http_status", None)
    if status is None or not 200 <= status < 300 or result.get("error"):
        return False
    errcode = result.get("errcode")
    if errcode is None:
        return True
    if isinstance(errcode, str):
        errcode = errcode.strip()
        if not errcode:
            return True
        if len(errcode) != 3 or not errcode.isascii() or not errcode.isdigit():
            return False
        errcode = int(errcode)
    return type(errcode) in (int, float) and 200 <= errcode < 300 and errcode % 1 == 0

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

# ===== LinkFox 统一输出层（落盘 + 摘要，无缓存）=====
# 本模块提供输出辅助函数，供各入口脚本调用 emit_result()。
# 依赖：json, os, sys, time, secrets, tempfile（共享模块通常已 import json/os/sys；
#       若缺 time/secrets/tempfile，请在文件顶部补 import）。

import time as _lf_time
import secrets as _lf_secrets

LF_SMALL_THRESHOLD = 8000
_LF_SESSION_CACHE: dict = {}

SLUG = "linkfox-temu-cancel-order-us"


def _lf_root() -> str:
    """业务入口仅使用当前目录；不可写时在请求前报错。"""
    root = Path.cwd() / "linkfox"
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(dir=root):
        pass
    return str(root.resolve())


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
    if isinstance(result, _GatewayResult):
        print(result.cli_output, end="")
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
